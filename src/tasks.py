from sqlmodel import Session, select
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
                payment = PaymentInfo(main_id=main_id, user_id=user_id, transaction_amount=amount, is_valid=False)
                session.add(payment)
                session.commit()
                return False

            user.money -= amount
            user.on_hold_money += amount

            payment = PaymentInfo(main_id=main_id, user_id=user_id, transaction_amount=amount, is_valid=True)
            session.add(payment)

            session.commit()
            return True
        except SQLAlchemyError as e:
            payment = PaymentInfo(main_id=main_id, user_id=user_id, transaction_amount=amount, is_valid=False)
            session.add(payment)
            session.commit()
            return False


@app.task
def rollback_payment(main_id, reason) -> bool:
    engine = get_engine()
    try:
        with Session(engine) as session:
            # gets corresponding payment info and user
            statement = select(PaymentInfo).where(PaymentInfo.main_id == main_id)
            payment_info = session.exec(statement).one()
            statement = select(UserMoney).where(UserMoney.user_id == payment_info.user_id)
            user = session.exec(statement).one()

            # revert money on hold to user's money
            user.money += payment_info.transaction_amount
            user.on_hold_money -= payment_info.transaction_amount
            payment_info.is_valid = False

            # commit
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(e)
        return False


@app.task
def update_success(main_id: int) -> bool:
    engine = get_engine()
    try:
        with Session(engine) as session:
            # gets corresponding payment info and user
            statement = select(PaymentInfo).where(PaymentInfo.main_id == main_id)
            payment_info = session.exec(statement).one()
            statement = select(UserMoney).where(UserMoney.user_id == payment_info.user_id)
            user = session.exec(statement).one()

            # update user money
            user.on_hold_money -= payment_info.transaction_amount

            # commit
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(e)
        return False


if __name__ == '__main__':
    from src.database.engine import create_db_and_tables

    # inputs are so that we can have pauses
    create_db_and_tables()
    print("Create payment of 36 money")
    print(create_payment(0, 1, 12, 3))  # True
    input()

    print("Create payment of 150 money")
    print(create_payment(1, 1, 50, 3))  # False
    input()

    print("Rollback payment of 36 money")
    print(rollback_payment(0, "test"))
    input()

    print("Create payment of 30 money")
    print(create_payment(2, 1, 10, 3))  # True
    input()

    print("Update success of 30 money")
    print(update_success(2))  # True
