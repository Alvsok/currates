from fastapi import FastAPI, Depends
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
from .database import get_db, Base  

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


