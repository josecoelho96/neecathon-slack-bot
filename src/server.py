import common
import exceptions
import handlers
import json
import logging as log
from bottle import Bottle, response, run
from definitions import SERVER_PORT


common.setup_logger()

class JSONBottle(Bottle):
    """Extension to default Bottle. All error messages are JSON formatted."""
    def default_error_handler(self, res):
        log.error("Server Error - Code: {} - Message: {}".format(res.status_code, res.body))
        response.add_header("Content-Type", "application/json")
        return json.dumps(dict(message = res.body, status_code = res.status_code))

def start():
    """Start HTTP server."""
    bot_app = JSONBottle()
    log.info("Starting HTTP server on port {}.".format(SERVER_PORT))
    try:
        define_routing(bot_app)
        run(app = bot_app, host="0.0.0.0", port=SERVER_PORT)
    except Exception as ex:
        log.error("Error: {}".format(ex))
        raise exceptions.HTTPServerStartError("HTTP server failed.")

def define_routing(app):
    """Defines all server routing scheme."""
    app.route(path="/create-team", method=["POST"], callback=handlers.create_team)