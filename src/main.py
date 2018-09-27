#!/usr/bin/env python3

import common
import exceptions
import logging as logger
import server
import dispatcher
import log_messages as messages
import slackapi


def main():
    common.setup_logger()
    logger.info(messages.SERVER_STARTING)
    if not slackapi.logger_info(messages.SERVER_STARTING):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    try:
        # Start dispatcher
        dispatcher.start()
        # Start http server
        server.start()
    except Exception as ex:
        logger.error(messages.HTTP_SERVER_STOPPED.format(ex))
        if not slackapi.logger_error(messages.HTTP_SERVER_STOPPED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)

if __name__ == "__main__":
    main()
