#!/usr/bin/env python3

import json
import logging as log

from bottle import Bottle, response, run

class JSONBottle(Bottle):
    def default_error_handler(self, res):
        log.warn("Error - Code: {} - Message: {}".format(res.status_code, res.body))
        response.add_header("Content-Type", "application/json")
        return json.dumps(dict(message = res.body, status_code = res.status_code))

def balance_handler():
    log.info("New balance consult request.")
    response.add_header("Content-Type", "application/json")
    response_content = {
            "text": "O meu assistente está a trabalhar no teu pedido...",
        }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

bot_app = JSONBottle()
bot_app.route(path="/balance", method=["POST"], callback=balance_handler)

def main():
    log.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s',
        level=log.DEBUG
    )
    run(app = bot_app, host="0.0.0.0", port=8000, reloader=True)

if __name__ == "__main__":
    main()