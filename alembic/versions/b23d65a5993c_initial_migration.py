"""Initial migration

Revision ID: b23d65a5993c
Revises: 
Create Date: 2024-02-20 10:59:53.920868

"""
from typing import Sequence, Union
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer
from alembic import op
import sqlalchemy as sa
from currency_init import currencies


# revision identifiers, used by Alembic.
revision: str = 'b23d65a5993c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создание таблицы Currency
    op.create_table('currency',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('code', sa.String(length=3), nullable=False, unique=True),
                    sa.Column('name', sa.String(length=50), nullable=True)
                    )

    # Создание таблицы ExchangeRate
    op.create_table('exchange_rate',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('success', sa.Boolean(), nullable=True),
                    sa.Column('timestamp', sa.Integer(), nullable=True),
                    sa.Column('base_id', sa.Integer(), sa.ForeignKey('currency.id'), nullable=True),
                    sa.Column('date', sa.Date(), nullable=True)
                    )

    # Создание таблицы CurrencyRate
    op.create_table('currency_rate',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('exchange_rate_id', sa.Integer(), sa.ForeignKey('exchange_rate.id'), nullable=False),
                    sa.Column('currency_id', sa.Integer(), sa.ForeignKey('currency.id'), nullable=False),
                    sa.Column('rate', sa.Numeric(20, 6), nullable=True)
                    )

    # Заполнение таблицы Currency данными
    currency_table = table('currency',
                           column('code', String),
                           column('name', String)
                           )

    op.bulk_insert(currency_table, currencies)


def downgrade():
    # Удаление таблиц в обратной последовательности их создания
    op.drop_table('currency_rate')
    op.drop_table('exchange_rate')
    op.drop_table('currency')
