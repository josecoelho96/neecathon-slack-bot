import logging as log
import responder
import dispatcher
from threading import Thread
from bottle import request
from definitions import SLACK_REQUEST_DATA_KEYS
import common

common.setup_logger()

def create_team():
    """Handler to create team request."""
    log.debug("New create team request.")
    request_data = dict(request.POST)

    if all_elements_on_request(request_data):
        # Procceed with request.
        log.debug("Request with correct fields, add to queue.")
        if dispatcher.add_request_to_queue(request_data):
            # Request was added to queue
            return responder.confirm_create_team_command_reception()
        else:
            # Request wasn't added to queue
            return responder.overloaded_error()
    else:
        # Inform user of incomplete request.
        log.warn("Request with invalid payload was sent.")
        return responder.default_error()

def join_team():
    """Handler to join team request."""
    log.debug("New join team request.")
    request_data = dict(request.POST)

    if all_elements_on_request(request_data):
        # Procceed with request.
        log.debug("Request with correct fields, add to queue.")
        if dispatcher.add_request_to_queue(request_data):
            # Request was added to queue
            return responder.confirm_join_team_command_reception()
        else:
            # Request wasn't added to queue
            return responder.overloaded_error()
    else:
        # Inform user of incomplete request.
        log.warn("Request with invalid payload was sent.")
        return responder.default_error()

def check_balance():
    """Handler to check balance request."""
    log.debug("New check balance request.")
    request_data = dict(request.POST)

    if all_elements_on_request(request_data):
        # Procceed with request.
        log.debug("Request with correct fields, add to queue.")
        if dispatcher.add_request_to_queue(request_data):
            # Request was added to queue
            return responder.confirm_check_balance_command_reception()
        else:
            # Request wasn't added to queue
            return responder.overloaded_error()
    else:
        # Inform user of incomplete request.
        log.warn("Request with invalid payload was sent.")
        return responder.default_error()

def buy():
    """Handler to buy request."""
    log.debug("New buy request.")
    request_data = dict(request.POST)

    if all_elements_on_request(request_data):
        # Procceed with request.
        log.debug("Request with correct fields, add to queue.")
        if dispatcher.add_request_to_queue(request_data):
            # Request was added to queue
            return responder.confirm_buy_command_reception()
        else:
            # Request wasn't added to queue
            return responder.overloaded_error()
    else:
        # Inform user of incomplete request.
        log.warn("Request with invalid payload was sent.")
        return responder.default_error()

def list_transactions():
    """Handler to list transactions request."""
    log.debug("New list transactions request.")
    request_data = dict(request.POST)

    if all_elements_on_request(request_data):
        # Procceed with request.
        log.debug("Request with correct fields, add to queue.")
        if dispatcher.add_request_to_queue(request_data):
            # Request was added to queue
            return responder.confirm_list_transactions_command_reception()
        else:
            # Request wasn't added to queue
            return responder.overloaded_error()
    else:
        # Inform user of incomplete request.
        log.warn("Request with invalid payload was sent.")
        return responder.default_error()

def all_elements_on_request(request_data):
    """Check if all elements (keys) are present in the request dictionary"""
    if all(k in request_data for k in SLACK_REQUEST_DATA_KEYS):
        return True
    return False
