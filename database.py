import datetime
from typing import List

import pytz
from sqlalchemy.orm import sessionmaker

import badge
from models import *


def setup_db_connection():
    thread_engine = create_engine('sqlite:////britebadge.db?check_same_thread=False')
    Base.metadata.bind = thread_engine
    DBParent = sessionmaker(bind=thread_engine)
    db_session = DBParent()
    return db_session


def get_current_purchases(db_session) -> List[Purchase]:
    purchases = db_session.query(Purchase).filter().all()
    #return sorted(purchases, key=lambda x: x., reverse=False)
    return purchases


def get_last_check_time(db_session):
    last_checked_time = db_session.query(Configuration).filter(Configuration.config_key == "last_checked_time").first()
    f = '%Y-%m-%d %H:%M:%S%z'
    if last_checked_time:
        to_return = datetime.datetime.strptime(last_checked_time.config_value, f)
        last_checked_time.config_value = datetime.datetime.now(pytz.utc).strftime(f)
        db_session.commit()
        return to_return
    else:
        current_time = datetime.datetime.now(pytz.utc)
        t = Configuration(config_key="last_checked_time", config_value=current_time.strftime(f))
        db_session.add(t)
        db_session.commit()
        return datetime.datetime.now(pytz.utc) - datetime.timedelta(days=360)


def compare_purchases(db_session, current_purchases: List[Purchase], new_purchases: List[Purchase]):
    for new_purchase in new_purchases:
        for current_purchase in current_purchases:
            if new_purchase.purchase_uuid == current_purchase.purchase_uuid:
                break
                print("Updated {} from {} to {}".format(current_purchase.first_name, current_purchase.status, new_purchase.status))
                current_purchase.status = new_purchase.status
                print("Printing label")
                db_session.add(PrintQueue(name="", purchase_id=new_purchase.purchase_id, printed=False))

                db_session.commit()

                break
        else:
            db_session.add(new_purchase)
            badge.create_label_image(new_purchase)
    db_session.commit()


def get_next_print_queue_item(db_session) -> PrintQueue:
    queue_item = db_session.query(PrintQueue).filter(PrintQueue.printed == False).first()
    return queue_item


def mark_queue_item_as_printed(db_session, queue_item:PrintQueue):
    queue_item.printed = True
    db_session.commit()


def get_print_queue(db_session) -> List[PrintQueue]:
    queue = db_session.query(PrintQueue).all()
    return sorted(queue, key=lambda x: x.queue_id, reverse=True)


def clear_print_queue(db_session):
    db_session.query(PrintQueue).delete()
    db_session.commit()


def add_to_print_queue(db_session, puchase_id):
    purchase = db_session.query(Purchase).filter(Purchase.purchase_id == int(puchase_id)).first()
    #db_session.add()
    db_session.add(PrintQueue(name="Bob", purchase=purchase, printed=False))
    db_session.commit()