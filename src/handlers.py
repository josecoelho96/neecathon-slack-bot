import logging as logger
import responder
import dispatcher
from bottle import request
from definitions import SLACK_REQUEST_DATA_KEYS, SLACK_REQUEST_TIMESTAMP_MAX_GAP_SECONDS
import common
import time
import database
import exceptions
import hmac
import hashlib
import os
import log_messages as messages
import db_request_messages as db_messages
import slackapi


common.setup_logger()

def request_handler():
    """Handler to requests."""
    logger.debug(messages.REQUEST_RECEIVED)
    request_data = dict(request.POST)

    if check_request_origin(request):
        if all_elements_on_request(request_data):
            # Procceed with request.
            if dispatcher.add_request_to_queue(request_data):
                # Request was added to queue
                return responder.confirm_command_reception()
            else:
                # Request wasn't added to queue
                logger.critical(messages.SERVER_OVERLOADED_ERROR)
                if not slackapi.logger_critical(messages.SERVER_OVERLOADED_ERROR):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
                try:
                    database.save_request_log(request_data, False, db_messages.SERVER_OVERLOADED)
                except exceptions.SaveRequestLogError:
                    logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                return responder.overloaded_error()
        else:
            # Inform user of incomplete request.
            logger.error(messages.REQUEST_WITH_INVALID_PAYLOAD)
            if not slackapi.logger_error(messages.REQUEST_WITH_INVALID_PAYLOAD):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            # Is incomplete. Don't save on database.
            return responder.default_error()
    else:
        # Could not validate user request
        logger.error(messages.REQUEST_ORIGIN_CHECK_FAILED)
        if not slackapi.logger_error(messages.REQUEST_ORIGIN_CHECK_FAILED):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        if all_elements_on_request(request_data):
            try:
                database.save_request_log(request_data, False, db_messages.REQUEST_ORIGIN_CHECK_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        return responder.unverified_origin_error()

def all_elements_on_request(request_data):
    """Check if all elements (keys) are present in the request dictionary"""
    if all(k in request_data for k in SLACK_REQUEST_DATA_KEYS):
        return True
    return False

def check_request_origin(request):
    """Check if a request origin matches Slack definitions."""
    request_timestamp = request.get_header("X-Slack-Request-Timestamp")
    if request_timestamp:
        slack_signature = request.get_header("X-Slack-Signature")
        if slack_signature:
            if abs(float(request_timestamp) - time.time()) < SLACK_REQUEST_TIMESTAMP_MAX_GAP_SECONDS:
                # Request within gap
                request_body = request.body.read().decode("utf-8")
                signing_secret = bytes(os.getenv("SLACK_SIGNING_SECRET"), "utf-8")
                base_string = "v0:{}:{}".format(request_timestamp, request_body).encode("utf-8")
                computed_signature = "v0=" + hmac.new(signing_secret, msg = base_string, digestmod=hashlib.sha256).hexdigest()

                if hmac.compare_digest(slack_signature, computed_signature):
                    return True
                else:
                    logger.critical(messages.REQUEST_REFUSED_BAD_SIGNATURE)
                    return False
            else:
                logger.critical(messages.REQUEST_REFUSED_BAD_TIMESTAMP)
                return False
        else:
            # No header
            logger.critical(messages.REQUEST_REFUSED_NO_SIGNATURE_HEADER)
            return False
    else:
        logger.critical(messages.REQUEST_REFUSED_NO_TIMESTAMP_HEADER)
        return False
