import logging as log
import database
import responder
from threading import Thread
from queue import Queue
from definitions import SLACK_COMMANDS
import common
import exceptions
import uuid
import random
import string

common.setup_logger()

requests_queue = Queue()

def start():
    """Starts a request dispatcher thread."""
    log.debug("Starting dispatcher thread.")

    t = Thread(target=general_dispatcher, name="DispatcherThread")
    t.setDaemon(True)
    t.start()

def general_dispatcher():
    """Main dispatcher loop"""
    while True:
        request = requests_queue.get()
        log.debug("Process new request.")

        if request["command"] == SLACK_COMMANDS["CREATE_TEAM"]:
            create_team_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["JOIN_TEAM"]:
            join_team_dispatcher(request)
        else:
            log.critical("Invalid request command.")

        log.debug("Process request done.")
        requests_queue.task_done()

def create_team_dispatcher(request):
    """Dispatcher to create team requests/commands."""
    log.debug("Create team request.")
    team_name = request['text']

    if not team_name:
        log.warn("Bad format on command '{}': Not enough arguments."
            .format(request['command'])
        )
        try:
            database.save_request_log(request, False, "Not enough arguments.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.create_team_delayed_reply_missing_arguments(request)
        return

    try:
        if database.team_name_available(team_name):
            log.debug("Team name available.")
            [team_id, team_entry_code] = generate_team_details()
            try:
                database.save_team_registration(team_id, team_name, team_entry_code)
            except exceptions.QueryDatabaseError:
                log.critical("Could not save new team registration.")
                try:
                    database.save_request_log(request, False, "Could not save new team registration.")
                except exceptions.SaveRequestLogError:
                    log.error("Failed to save request log on database.")
                responder.default_error()
            else:
                log.debug("Team name saved.")
                try:
                    database.save_request_log(request, True, "New team registration saved successfully.")
                except exceptions.SaveRequestLogError:
                    log.error("Failed to save request log on database.")
                responder.create_team_delayed_reply_success(request, team_id, team_name, team_entry_code)
        else:
            log.debug("Team name already picked.")
            try:
                database.save_request_log(request, False, "Team name already exists.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.create_team_delayed_reply_name_exists(request, team_name)
    except exceptions.QueryDatabaseError:
        log.critical("Can't verify team name.")
        try:
            database.save_request_log(request, False, "Could not verify team name.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()

def join_team_dispatcher(request):
    """Dispatcher to join team requests/commands."""
    log.debug("Join team request.")
    team_entry_code = request["text"]
    if not team_entry_code:
        log.warn("Bad format on command '{}': Not enough arguments."
            .format(request['command'])
        )
        try:
            database.save_request_log(request, False, "Not enough arguments.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.join_team_delayed_reply_missing_arguments(request)
        return

    # Check if user is in the users table
    try:
        if not database.user_exists(request['user_id']):
            log.debug("New user.")
            # Save new user.
            database.save_user(request["user_id"], request["user_name"], generate_uuid4())
    except exceptions.QueryDatabaseError as ex:
        log.critical("User search failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform user search.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return

    # Check if user has a team
    log.debug("Checking if user has a team.")
    try:
        if database.user_has_team(request["user_id"]):
            # User already on team.
            log.info("User is already on a team.")
            responder.join_team_delayed_reply_already_on_team(request)
            try:
                database.save_request_log(request, False, "User already on team.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            return
    except exceptions.QueryDatabaseError as ex:
        log.critical("User team search failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform user's team search.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return

    # Check if provided code is valid
    log.debug("User has no team: Add user to team if code is valid.")
    team_info = {}
    try:
        team_info = database.valid_entry_code(team_entry_code)
        if not team_info:
            log.warning("Invalid entry code provided.")
            responder.join_team_delayed_reply_invalid_code(request)
            try:
                database.save_request_log(request, False, "Invalid entry code.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            return
    except exceptions.QueryDatabaseError as ex:
        log.critical("Entry code validation failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform entry code validation.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return

    log.debug("Valid code - Team: {}".format(team_info))
    try:
        # Check if team already created.
        if not database.is_team_created(team_info["id"]):
            log.debug("Create new team.")
            try:
                database.create_team(team_info["id"], team_info["name"])
            except exceptions.QueryDatabaseError as ex:
                log.critical("Team creation failed: {}".format(ex))
                try:
                    database.save_request_log(request, False, "Could not perform team creation.")
                except exceptions.SaveRequestLogError:
                    log.error("Failed to save request log on database.")
                responder.default_error()
                return
    except exceptions.QueryDatabaseError as ex:
        log.critical("Team search failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform team search.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return

    log.debug("Add user to team.")
    try:
        database.add_user_to_team(request["user_id"], team_info["id"])
    except exceptions.QueryDatabaseError as ex:
        log.critical("User addition to team failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not add user to team (team created).")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
    else:
        log.info("User joined team.")
        try:
            database.save_request_log(request, True, "User joined team.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.join_team_delayed_reply_success(request, team_info["name"])

def add_request_to_queue(request):
    """ Add a request to the requests queue."""
    try:
        requests_queue.put(request, block=False)
    except Exception:
        log.error("Requests queue is full. Request will be discarded")
        return False
    else:
        return True

def generate_team_details():
    """ Generates and returns a team ID and team entry code."""
    team_id = generate_uuid4()
    team_entry_code = "-".join([generate_random_code(), generate_random_code()])
    return [team_id, team_entry_code]

def generate_random_code(n = 4):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

def generate_uuid4():
    return str(uuid.uuid4())