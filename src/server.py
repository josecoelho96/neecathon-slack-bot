#!/usr/bin/env python3

import json
import logging as log
import time
import threading

from bottle import abort, Bottle, response, request, run
from queue import Queue
from threading import Thread

# Requests must contain all this keys to be valid
SLACK_REQUEST_DATA_KEYS = [
    "token",
    "team_id",
    "team_domain",
    "channel_id",
    "channel_name",
    "user_id",
    "user_name",
    "text",
    "response_url",
]

SERVER_PORT = 8888

requests_queue = Queue()

class JSONBottle(Bottle):
    def default_error_handler(self, res):
        log.warn("Error - Code: {} - Message: {}".format(res.status_code, res.body))
        response.add_header("Content-Type", "application/json")
        return json.dumps(dict(message = res.body, status_code = res.status_code))

def balance_handler():
    log.info("New balance consult request.")
    request_body = dict(request.POST)
    log.debug(request_body)
    if (valid_request_data(request_body)):
        log.debug("Valid load, add request to queue.")
        requests_queue.put(request_body)
        response.add_header("Content-Type", "application/json")
        response_content = {
                "text": "O meu assistente está a trabalhar no teu pedido...",
            }
        return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

    else:
        log.info("Request with invalid payload was sent.")
        abort(400, "Bad request: Wrong payload")

    response.add_header("Content-Type", "application/json")
    response_content = {
            "text": "O meu assistente está a trabalhar no teu pedido...",
        }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def valid_request_data(request_data):
    if all(k in request_data for k in SLACK_REQUEST_DATA_KEYS):
        return True
    return False

def start_server():
    log.info("Starting server on port {}".format(SERVER_PORT))
    run(app = bot_app, host="0.0.0.0", port=SERVER_PORT)

def start_dispatcher_thread():
    log.info("Starting dispatcher thread.")
    t = Thread(target=dispatch_requests, name="DispatcherThread")
    t.setDaemon(True)
    t.start()

def dispatch_requests():
    while True:
        request = requests_queue.get()
        log.debug("Process new request by Thread: {}...".format(threading.current_thread().getName()))
        time.sleep(10)
        log.debug("Process request done on Thread: {}...".format(threading.current_thread().getName()))
        requests_queue.task_done()

bot_app = JSONBottle()
bot_app.route(path="/balance", method=["POST"], callback=balance_handler)

def main():
    log.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s',
        level=log.DEBUG
    )
    start_dispatcher_thread()
    start_server()

if __name__ == "__main__":
    main()