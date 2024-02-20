from sqlalchemy import Column, String, Numeric, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, nullable=False)
    name = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Currency(code='{self.code}', name='{self.name}')>"


class ExchangeRate(Base):
    __tablename__ = 'exchange_rate'

    id = Column(Integer, primary_key=True)
    success = Column(Boolean, default=True)
    timestamp = Column(Integer)
    base_id = Column(Integer, ForeignKey('currency.id'), nullable=True)
    date = Column(Date)

    base = relationship("Currency", backref="base_rates")

    def __repr__(self):
        return f"<ExchangeRate(base='{self.base.code}', date='{self.date}')>"


class CurrencyRate(Base):
    __tablename__ = 'currency_rate'

    id = Column(Integer, primary_key=True)
    exchange_rate_id = Column(Integer, ForeignKey('exchange_rate.id'), nullable=False)
    currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False)
    rate = Column(Numeric(20, 6))

    exchange_rate = relationship("ExchangeRate", backref="rates")
    currency = relationship("Currency", backref="currency_rates")

    def __repr__(self):
        return f"<CurrencyRate(currency='{self.currency.code}', rate='{self.rate}')>"
