from dotenv import load_dotenv
import os
from datetime import datetime
from decimal import Decimal, getcontext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
import httpx
from .models import Currency, ExchangeRate, CurrencyRate

getcontext().prec = 6
load_dotenv()


async def add_currency_rate(session: AsyncSession):

    ACCESS_KEY = os.getenv("ACCESS_KEY")
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key={ACCESS_KEY}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    if response.status_code != 200:
        raise ValueError(response)

    base_currency_stmt = select(Currency).where(Currency.code == data['base'])
    base_currency_result = await session.execute(base_currency_stmt)
    base_currency = base_currency_result.scalars().first()

    if not base_currency:
        raise ValueError(f"Base currency {data['base']} not found in the database")

    exchange_rate = ExchangeRate(
        success=data['success'],
        timestamp=data['timestamp'],
        base_id=base_currency.id,
        date=datetime.strptime(data['date'], '%Y-%m-%d').date()
    )
    session.add(exchange_rate)
    await session.flush()

    for currency_code, rate in data['rates'].items():
        currency_stmt = select(Currency).where(Currency.code == currency_code)
        currency_result = await session.execute(currency_stmt)
        currency = currency_result.scalars().first()

        if currency:
            currency_rate = CurrencyRate(
                exchange_rate_id=exchange_rate.id,
                currency_id=currency.id,
                rate=rate
            )
            session.add(currency_rate)

    await session.commit()


async def get_latest_update_info(db: AsyncSession) -> str:
    stmt = select(ExchangeRate).order_by(desc(ExchangeRate.timestamp)).limit(1)
    result = await db.execute(stmt)
    latest_exchange_rate = result.scalars().first()

    if latest_exchange_rate is None:
        return "There are no records of exchange rates in the database yet."

    latest_update_datetime = datetime.utcfromtimestamp(latest_exchange_rate.timestamp)
    return f"The last update of courses in the database occurred {latest_update_datetime.strftime('%Y-%m-%d %H:%M:%S')} UTC"


async def convert_currency(session: AsyncSession, source_code: str, target_code: str, amount: float) -> str:
    source_code = source_code.upper()
    target_code = target_code.upper()

    latest_exchange_rate_stmt = select(ExchangeRate).order_by(desc(ExchangeRate.timestamp)).limit(1)
    latest_exchange_rate_result = await session.execute(latest_exchange_rate_stmt)
    latest_exchange_rate = latest_exchange_rate_result.scalars().first()

    if not latest_exchange_rate:
        return "No exchange rates found in the database."

    source_currency_stmt = select(Currency).where(Currency.code == source_code)
    target_currency_stmt = select(Currency).where(Currency.code == target_code)

    source_currency = (await session.execute(source_currency_stmt)).scalars().first()
    target_currency = (await session.execute(target_currency_stmt)).scalars().first()

    if not source_currency or not target_currency:
        return "One of the currency codes is invalid."

    source_rate_stmt = select(CurrencyRate.rate).where(CurrencyRate.currency_id ==
                                                       source_currency.id, CurrencyRate.exchange_rate_id == latest_exchange_rate.id)
    target_rate_stmt = select(CurrencyRate.rate).where(CurrencyRate.currency_id ==
                                                       target_currency.id, CurrencyRate.exchange_rate_id == latest_exchange_rate.id)

    source_rate = (await session.execute(source_rate_stmt)).scalars().first()
    target_rate = (await session.execute(target_rate_stmt)).scalars().first()

    if not source_rate or not target_rate:
        return "Could not find exchange rates for the provided currency codes."

    amount_decimal = Decimal(str(amount))
    source_rate_decimal = Decimal(str(source_rate))
    target_rate_decimal = Decimal(str(target_rate))

    converted_amount = (amount_decimal / source_rate_decimal) * target_rate_decimal
    latest_update_datetime = datetime.utcfromtimestamp(latest_exchange_rate.timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

    return f"{amount} in {source_currency.name} as of {latest_update_datetime} is equivalent to {converted_amount:.2f} in {target_currency.name}."
