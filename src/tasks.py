from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from celery.exceptions import SoftTimeLimitExceeded

from src import app, result_collector
from src.database.engine import get_engine
from src.database.models import UserMoney, PaymentInfo

RESULT_TASK_NAME = "wk-irs.tasks.send_result"

@app.task(
    soft_time_limit=30, 
    time_limit=60,
    name='wk-payment.tasks.create_payment'
)
def create_payment(**kwargs) -> bool:
    main_id = kwargs.get('main_id', None)
    user_id = kwargs.get('user_id', None)
    item_price = kwargs.get('item_price', None)
    quantity = kwargs.get('quantity', None)
    
    engine = get_engine()
    success = True
    with Session(engine) as session:
        amount = item_price * quantity
        try:
            user = session.get(UserMoney, user_id)
            if user is None:
                user = UserMoney(user_id=user_id)
                session.add(user)
                session.commit()

            if user.money < amount:
                payment = PaymentInfo(main_id=main_id, user_id=user_id, transaction_amount=amount, is_valid=False)
                session.add(payment)
                session.commit()
                raise ValueError("Insufficient funds")

            user.money -= amount
            user.on_hold_money += amount

            payment = PaymentInfo(main_id=main_id, user_id=user_id, transaction_amount=amount, is_valid=True)
            session.add(payment)

            session.commit()
        except SQLAlchemyError as e:
            payment = PaymentInfo(main_id=main_id, user_id=user_id, transaction_amount=amount, is_valid=False)
            session.add(payment)
            session.commit()
            kwargs["error"] = str(e)
        except ValueError as e:
            success = False
            kwargs["error"] = "insufficient_funds"
        except SoftTimeLimitExceeded:
            success = False
            kwargs["error"] = "timeout"
        except Exception as e:
            success = False
            kwargs["error"] = str(e)
        
        result_object = {
            "main_id": main_id,
            "success": success,
            "service_name": "payment",
            "payload": kwargs,
        }
        result_collector.send_task(
            RESULT_TASK_NAME,
            kwargs=result_object,
            task_id=str(main_id)
        )
        return success


@app.task(name='wk-payment.tasks.rollback')
def rollback_payment(**kwargs) -> bool:
    main_id = kwargs.get('main_id', None)
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
    except SQLAlchemyError as e:
        kwargs["error"] = str(e)
    
    result_object = {
        "main_id": main_id,
        "success": False, # this is for triggering the rollback on the backend
        "service_name": "payment",
        "payload": kwargs,
    }
    result_collector.send_task(
        RESULT_TASK_NAME,
        kwargs=result_object,
        task_id=str(main_id)
    )
    return False


@app.task(
    soft_time_limit=30, 
    time_limit=60,
    name='wk-payment.tasks.confirm_payment'
)
def update_success(**kwargs) -> bool:
    main_id = kwargs.get('main_id', None)
    engine = get_engine()
    success = True
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
    except SoftTimeLimitExceeded:
        success = False
        kwargs["error"] = "timeout"
    except Exception as e:
        success = False
        kwargs["error"] = str(e)
    
    result_object = {
        "main_id": main_id,
        "success": success,
        "service_name": "payment_final",
        "payload": kwargs,
    }
    result_collector.send_task(
        RESULT_TASK_NAME,
        kwargs=result_object,
        task_id=str(main_id)
    )
    return success


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
