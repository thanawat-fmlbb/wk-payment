from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from src import app
from src.database.engine import get_engine
from src.database.models import UserMoney, PaymentInfo


@app.task
def create_payment(main_id, user_id: int, item_price: int, quantity: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        amount = item_price * quantity
        try:
            user = session.get(UserMoney, user_id)
            if user is None:
                user = UserMoney(user_id=user_id)
                session.add(user)

            if user.money < amount:
                session.rollback()
                return False

            user.money -= amount
            user.on_hold_money += amount

            payment = PaymentInfo(main_id=main_id, transaction_amount=amount, is_valid=True)
            session.add(payment)

            session.commit()
            return True
        except SQLAlchemyError as e:
            payment = PaymentInfo(main_id=main_id, transaction_amount=amount, is_valid=False)
            session.add(payment)
            session.commit()
            return False


@app.task
def rollback_payment(main_id, reason):
    ...


if __name__ == '__main__':
    print(create_payment(0, 1, 12, 3))
    input()
    print(create_payment(1, 1, 50, 3))
