import logging as log
import responder
import dispatcher
from threading import Thread
from bottle import request
from definitions import SLACK_REQUEST_DATA_KEYS, SLACK_REQUEST_TIMESTAMP_MAX_GAP_MINUTES
import common
import time
import database
import exceptions
import hmac
import hashlib
import os


common.setup_logger()

def create_team():
    """Handler to create team request."""
    log.debug("New create team request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
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
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
        return responder.unverified_origin_error()

def join_team():
    """Handler to join team request."""
    log.debug("New join team request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
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
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
        return responder.unverified_origin_error()

def check_balance():
    """Handler to check balance request."""
    log.debug("New check balance request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
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
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
        return responder.unverified_origin_error()

def buy():
    """Handler to buy request."""
    log.debug("New buy request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
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
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
        return responder.unverified_origin_error()

def list_transactions():
    """Handler to list transactions request."""
    log.debug("New list transactions request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
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
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
        return responder.unverified_origin_error()

def list_teams():
    """Handler to list teams request."""
    log.debug("New list teams request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
        if all_elements_on_request(request_data):
            # Procceed with request.
            log.debug("Request with correct fields, add to queue.")
            if dispatcher.add_request_to_queue(request_data):
                # Request was added to queue
                return responder.confirm_list_teams_command_reception()
            else:
                # Request wasn't added to queue
                return responder.overloaded_error()
        else:
            # Inform user of incomplete request.
            log.warn("Request with invalid payload was sent.")
            return responder.default_error()
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
        return responder.unverified_origin_error()

def list_teams_registration():
    """Handler to list teams registration request."""
    log.debug("New list teams registration request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
        if all_elements_on_request(request_data):
            # Procceed with request.
            log.debug("Request with correct fields, add to queue.")
            if dispatcher.add_request_to_queue(request_data):
                # Request was added to queue
                return responder.confirm_list_teams_registration_command_reception()
            else:
                # Request wasn't added to queue
                return responder.overloaded_error()
        else:
            # Inform user of incomplete request.
            log.warn("Request with invalid payload was sent.")
            return responder.default_error()
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
        return responder.unverified_origin_error()

def team_details():
    """Handler to list a team details."""
    log.debug("New team details request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
        if all_elements_on_request(request_data):
            # Procceed with request.
            log.debug("Request with correct fields, add to queue.")
            if dispatcher.add_request_to_queue(request_data):
                # Request was added to queue
                return responder.confirm_team_details_command_reception()
            else:
                # Request wasn't added to queue
                return responder.overloaded_error()
        else:
            # Inform user of incomplete request.
            log.warn("Request with invalid payload was sent.")
            return responder.default_error()
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
        return responder.unverified_origin_error()

def user_details():
    """Handler to list a user details."""
    log.debug("New user details request.")
    request_data = dict(request.POST)

    if check_request_origin(request):
        if all_elements_on_request(request_data):
            # Procceed with request.
            log.debug("Request with correct fields, add to queue.")
            if dispatcher.add_request_to_queue(request_data):
                # Request was added to queue
                return responder.confirm_user_details_command_reception()
            else:
                # Request wasn't added to queue
                return responder.overloaded_error()
        else:
            # Inform user of incomplete request.
            log.warn("Request with invalid payload was sent.")
            return responder.default_error()
    else:
        # Could not validate user request
        log.error("Slack request origin verification failed.")
        try:
            database.save_request_log(request_data, False, "Unverified origin.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log.")
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
            if abs(float(request_timestamp) - time.time()) < SLACK_REQUEST_TIMESTAMP_MAX_GAP_MINUTES:
                # Request within gap
                request_body = request.body.read().decode("utf-8")
                signing_secret = bytes(os.getenv("SLACK_SIGNING_SECRET"), "utf-8")
                base_string = "v0:{}:{}".format(request_timestamp, request_body).encode("utf-8")
                computed_signature = "v0=" + hmac.new(signing_secret, msg = base_string, digestmod=hashlib.sha256).hexdigest()

                if hmac.compare_digest(slack_signature, computed_signature):
                    log.debug("Request origin verified.")
                    return True
                else:
                    log.critical("'X-Slack-Signature' header value and computed signature don't match.")
                    return False
            else:
                log.critical("Header 'X-Slack-Request-Timestamp' value is different than handler server. Refusing request.")
                log.debug("Header value: {} | Current timestamp: {}".format(request_timestamp, time.time()))
                return False
        else:
            # No header
            log.critical("Header 'X-Slack-Signature' not present. Refusing request.")
            return False
    else:
        log.critical("Header 'X-Slack-Request-Timestamp' not present. Refusing request.")
        return False
