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
    team_id = str(uuid.uuid4())
    team_entry_code = "-".join([generate_random_code(), generate_random_code()])
    return [team_id, team_entry_code]

def generate_random_code(n = 4):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))