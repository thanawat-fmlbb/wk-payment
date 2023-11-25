from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from src import app
from src.database.engine import get_engine
from src.database.models import UserMoney


@app.task
def create_payment(main_id, user_id: int, item_price: int, quantity: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        try:
            user = session.get(UserMoney, user_id)
            if user is None:
                user = UserMoney(user_id=user_id)
                session.add(user)

            if user.money < item_price * quantity:
                session.rollback()
                return False

            user.money -= item_price * quantity
            user.on_hold_money += item_price * quantity
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            return False


@app.task
def rollback_payment(main_id, reason):
    ...


if __name__ == '__main__':
    print(create_payment(0, 1, 12, 3))
    input()
    print(create_payment(0, 1, 50, 3))
