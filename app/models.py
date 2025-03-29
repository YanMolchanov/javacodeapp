from sqlmodel import Field, SQLModel
from pydantic import BaseModel
from typing import Literal


class WalletBase(SQLModel):
    balance: float = Field(title='Баланс кошелька', ge=0)


class Wallet(WalletBase, table=True):
    id: int | None = Field(default=None, title='id кошелька', primary_key=True)


class WalletPublic(WalletBase):
    id: int


class FilterParams(BaseModel):
    operation_type: Literal['DEPOSIT', 'WITHDRAW']
    operation_sum: float = Field(default=0, title='Сумма операции', gt=0)


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)
