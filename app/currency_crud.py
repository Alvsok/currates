from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Currency
from .schemas import CurrencyCreate, CurrencyUpdate


async def create_currency(db: AsyncSession, currency_data: CurrencyCreate) -> Currency:
    new_currency = Currency(**currency_data.dict())
    db.add(new_currency)
    await db.commit()
    await db.refresh(new_currency)
    return new_currency


async def get_currency(db: AsyncSession, currency_id: int) -> Currency:
    async with db as session:
        result = await session.execute(select(Currency).filter(Currency.id == currency_id))
        currency = result.scalars().first()
        return currency


async def get_currencies(db: AsyncSession) -> list[Currency]:
    async with db as session:
        result = await session.execute(select(Currency))
        currencies = result.scalars().all()
        return currencies


async def update_currency(db: AsyncSession, currency_id: int, currency_data: CurrencyUpdate) -> Currency:
    db_currency = await get_currency(db, currency_id)
    for key, value in currency_data.dict().items():
        setattr(db_currency, key, value)
    await db.commit()
    await db.refresh(db_currency)
    return db_currency


async def delete_currency(db: AsyncSession, currency_id: int):
    db_currency = await get_currency(db, currency_id)
    await db.delete(db_currency)
    await db.commit()
