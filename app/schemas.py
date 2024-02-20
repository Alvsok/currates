from pydantic import BaseModel, constr

class CurrencyBase(BaseModel):
    code: constr(max_length=3)
    name: str

class CurrencyCreate(CurrencyBase):
    pass

class CurrencyUpdate(CurrencyBase):
    code: constr(max_length=3) = None
    name: str = None

class Currency(CurrencyBase):
    id: int

    class Config:
        orm_mode = True

