import json
import sys
import time

from flask import Flask, render_template, redirect, request

import database
try:
    import display
    display_lib = True
except:
    display_lib = False
    print("Unable to import display library, ignoring")

import models
from secrets.config import delay_between_zettle_queries, zettle_api_key, zettle_client_id
import zettle_api

import threading
import badge

import secrets.config as config

app = Flask(__name__)

flask_db_session = database.setup_db_connection()


class BackgroundPrinter(threading.Thread):

    def __init__(self):
        super().__init__()

        self.db_session = database.setup_db_connection()

    def run(self):
        while True:
            try:
                queue_item = database.get_next_print_queue_item(self.db_session)
                if queue_item:
                    print("PRINTING BADGE FOR {}".format(queue_item.name))
                    badge.create_label_image(queue_item.purchase)
                    database.mark_queue_item_as_printed(self.db_session, queue_item)
                else:
                    time.sleep(0.5)
            except UnicodeError as e:
                print("---------------")
                print("EXCEPTION!?!?!?")
                print(e)
                print("---------------")
                time.sleep(3)


class ZettleWatcher(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self.db_session = database.setup_db_connection()
    
    
    def run(self):
        if display_lib:
            display.write_ip()
        while True:
            try:
                if display_lib:
                    display.update_display()
            except Exception as e:
                print("---------------")
                print("EXCEPTION!?!?!?")
                print(e)
                print("---------------")
            self.update()

    def update(self):
        start_update = time.time()
        print("Checking for updates")
        new_purchases = zettle_api.get_purchases(changed_since=database.get_last_check_time(self.db_session))

        current_purchases = database.get_current_purchases(self.db_session)
        database.compare_purchases(self.db_session, current_purchases, new_purchases)
        print("Checking for updates from Zettle took {} seconds.".format(time.time() - start_update))
        if display_lib:
            display.update_display()

        # To be removed eventually when Javascript is making the queries to this endpoint
        time.sleep(int(delay_between_zettle_queries))


@app.route("/")
def home():
    orders = database.get_current_purchases(flask_db_session)
    return render_template("index.html", orders=orders)


@app.route("/print_queue")
def print_queue():
    return render_template("print_queue.html")


@app.route("/get_print_queue_ajax", methods=['GET', 'POST'])
def get_print_queue():
    queue = database.get_print_queue(flask_db_session)
    to_send = ([dict(queue_id=q.queue_id, name=q.name, purchase_id=q.purchase_id, printed=q.printed) for q in queue])
    return json.dumps(to_send)


@app.route("/add_badge_to_queue", methods=['GET', 'POST'])
def add_badge_to_queue():
    attendee_id = request.form["attendee_id"]
    database.add_to_print_queue(flask_db_session, attendee_id)
    return ""


@app.route("/complete_order", methods=['GET', 'POST'])
def complete_order():
    product_purchase_id = request.form["attendee_id"]
    database.mark_purchase_complete(flask_db_session, product_purchase_id)
    return ""


@app.route("/clear_print_queue")
def clear_print_queue():
    database.clear_print_queue(flask_db_session)
    return redirect("/print_queue")


if __name__ == '__main__':
    background_printer = BackgroundPrinter()
    background_printer.daemon = True
    background_printer.start()

    eventbrite_watcher = ZettleWatcher()
    eventbrite_watcher.daemon = True
    eventbrite_watcher.start()
    if display_lib:
        display.display_text("Zettle orders")
        display.display_text("Starting...", 0, 1)
    app.run(host='0.0.0.0', port=80)
