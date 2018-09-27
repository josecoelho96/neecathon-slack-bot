import common
import exceptions
import handlers
import json
import logging as logger
from bottle import Bottle, response, run
from definitions import SERVER_PORT
import log_messages as messages
import slackapi


common.setup_logger()

class JSONBottle(Bottle):
    """Extension to default Bottle. All error messages are JSON formatted."""
    def default_error_handler(self, res):
        logger.error(messages.SERVER_ERROR.format(res.status_code, res.body))
        if not slackapi.logger_error(messages.SERVER_ERROR.format(res.status_code, res.body)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)

        response.add_header("Content-Type", "application/json")
        return json.dumps(dict(message = res.body, status_code = res.status_code))

def start():
    """Start HTTP server."""
    bot_app = JSONBottle()
    logger.debug(messages.HTTP_SERVER_STARTING.format(SERVER_PORT))
    try:
        define_routing(bot_app)
        run(app = bot_app, host="0.0.0.0", port=SERVER_PORT)
    except Exception as ex:
        logger.error(messages.HTTP_SERVER_STARTUP_ERROR.format(ex))
        if not slackapi.logger_error(messages.HTTP_SERVER_STARTUP_ERROR.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        raise exceptions.HTTPServerStartError("HTTP server startup failed.")

def define_routing(app):
    """Defines all server routing scheme."""
    app.route(path="/", method=["POST"], callback=handlers.request_handler)
