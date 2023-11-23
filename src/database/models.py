from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer


class UserMoney(SQLModel, table=True):
    __tablename__ = "user_money"

    user_id: int = Field(sa_column=Column("user_id", Integer, primary_key=True, autoincrement=False))
    money: int
    on_hold_money: int


class PaymentInfo(SQLModel, table=True):
    __tablename__ = "payment_info"

    id: int = Field(default=None, primary_key=True)
    main_id: int
    transaction_amount: int
    is_valid: bool
