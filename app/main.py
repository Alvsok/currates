from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .schemas import CurrencyCreate, CurrencyUpdate, Currency as CurrencySchema
from .currency_crud import (
    create_currency as crud_create_currency,
    get_currency as crud_get_currency,
    get_currencies as crud_get_currencies,
    update_currency as crud_update_currency,
    delete_currency as crud_delete_currency,
)
from .database import get_db
from .utils import add_currency_rate, get_latest_update_info, convert_currency

app = FastAPI()


@app.post("/currencies/", response_model=CurrencySchema)
async def create_currency(currency_data: CurrencyCreate, db: AsyncSession = Depends(get_db)):
    return await crud_create_currency(db, currency_data)


@app.get("/currencies/", response_model=List[CurrencySchema])
async def read_currencies(db: AsyncSession = Depends(get_db)):
    return await crud_get_currencies(db)


@app.get("/currencies/{currency_id}", response_model=CurrencySchema)
async def read_currency(currency_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_get_currency(db, currency_id)


@app.put("/currencies/{currency_id}", response_model=CurrencySchema)
async def update_currency(currency_id: int, currency_data: CurrencyUpdate, db: AsyncSession = Depends(get_db)):
    return await crud_update_currency(db, currency_id, currency_data)


@app.delete("/currencies/{currency_id}")
async def delete_currency(currency_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_delete_currency(db, currency_id)


@app.post("/currency-rate/")
async def create_currency_rate_aed(db: AsyncSession = Depends(get_db)):
    """обновление курсов валют"""
    try:
        await add_currency_rate(db)
        return {"message": "Currency rates added successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/latest-exchange-rate-update/")
async def latest_exchange_rate_update(db: AsyncSession = Depends(get_db)):
    """данные о времени последнего изменения курсов"""
    try:
        message = await get_latest_update_info(db)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/convert/")
async def convert_endpoint(
        source_code: str = Query(..., description="Source currency code"),
        target_code: str = Query(..., description="Target currency code"),
        amount: float = Query(..., description="Amount to convert"),
        db: AsyncSession = Depends(get_db)):
    """конвертация валют"""
    try:
        result = await convert_currency(db, source_code, target_code, amount)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
