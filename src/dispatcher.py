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
import re
import uuid
import security


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
        elif request["command"] == SLACK_COMMANDS["CHECK_BALANCE"]:
            check_balance_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["BUY"]:
            buy_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["LIST_TRANSACTIONS"]:
            list_transactions_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["LIST_TEAMS"]:
            list_teams_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["LIST_TEAMS_REGISTRATION"]:
            list_teams_registration_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["TEAM_DETAILS"]:
            team_details_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["USER_DETAILS"]:
            user_details_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["LIST_MY_TRANSACTIONS"]:
            list_my_transactions_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["CHANGE_PERMISSIONS"]:
            change_permissions_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["LIST_STAFF"]:
            list_staff_dispatcher(request)
        elif request["command"] == SLACK_COMMANDS["HACKERBOY"]:
            hackerboy_dispatcher(request)
        else:
            log.critical("Invalid request command.")

        log.debug("Process request done.")
        requests_queue.task_done()

def create_team_dispatcher(request):
    """Dispatcher to create team requests/commands."""
    log.debug("Create team request.")
    team_name = request['text']

    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        log.error("User has no permission to execute this command.")
        try:
            database.save_request_log(request, False, "Unauthorized.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.unauthorized_error(request)
        return

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

def check_balance_dispatcher(request):
    """Dispatcher to check balance requests/commands."""
    log.debug("Check balance request.")
    # First, check if user is in a team
    try:
        if not database.user_has_team(request["user_id"]):
            # User has no team
            log.debug("User has no team.")
            responder.check_balance_delayed_reply_no_team(request)
            try:
                database.save_request_log(request, False, "User has no team.")
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

    # If has a team, get the team balance
    log.debug("Check balance!")
    try:
        [team_name, team_balance] = database.get_users_balance(request["user_id"])
    except exceptions.QueryDatabaseError as ex:
        log.critical("User's team balance check failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform user's team balance search.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return
    else:
        log.debug("Report data to user.")
        responder.check_balance_delayed_reply_success(request, team_name, team_balance)
        try:
            database.save_request_log(request, True, "Balance retrieved successfully.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")

def buy_dispatcher(request):
    """Dispatcher to buy requests/commands."""
    log.debug("Buy request.")

    # Check if args are present
    request_args = get_request_args(request["text"])
    log.debug(request_args)

    if not request_args or len(request_args) < 3:
        log.warn("Bad format on command: '{}': Not enough arguments."
            .format(request["command"])
        )
        try:
            database.save_request_log(request, False, "Not enough arguments.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.buy_delayed_reply_missing_arguments(request)
        return

    # Check if user is in a team
    log.debug("Checking if user is in a team.")
    try:
        if not database.user_has_team(request["user_id"]):
            # User has no team
            log.debug("User has no team.")
            responder.delayed_reply_no_team(request)
            try:
                database.save_request_log(request, False, "User has no team.")
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

    # User has a team
    destination_slack_user_id = get_slack_user_id_from_arg(request_args[0])
    if not destination_slack_user_id:
        # User not present
        log.debug("No user was retrieved.")
        responder.buy_delayed_reply_no_user_arg(request)
        try:
            database.save_request_log(request, False, "Destination user not given.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        return
    log.info("Destination: {}".format(destination_slack_user_id))

    # Check if destination is valid (exists and has a team, not the same user and not in the same team)
    if request["user_id"] == destination_slack_user_id:
        log.warn("User tried to give money to himself.")
        responder.buy_delayed_reply_destination_himself(request)
        try:
            database.save_request_log(request, False, "Destination user is the donor itself.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        return

    try:
        if not database.user_has_team(destination_slack_user_id):
            # Destination user has no team
            log.debug("Destination user has no team.")
            responder.buy_delayed_reply_destination_no_team(request)
            try:
                database.save_request_log(request, False, "Destination user has no team.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            return
    except exceptions.QueryDatabaseError as ex:
        log.critical("User team search failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform destination user's team search.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return

    try:
        log.debug("Checking origin and destination teams.")
        if not database.users_with_different_team(destination_slack_user_id, request["user_id"]):
            log.warn("Users in same team.")
            responder.buy_delayed_reply_destination_same_team(request)
            try:
                database.save_request_log(request, False, "Destination user is in the same team as origin user.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            return
    except exceptions.QueryDatabaseError as ex:
        log.critical("Origin and destination users teams check failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform origin and destination users teams check.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return

    # Parse transaction value
    try:
        transaction_amount = parse_transaction_amount(request_args[1])
    except exceptions.FloatParseError as ex:
        log.critical("Failed to parse value to float.")
        try:
            database.save_request_log(request, False, "Could not perform amount value parsing.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.delayed_reply_invalid_value(request)
        return

    # Check if value is positive
    if transaction_amount <= 0:
        log.error("Non positive transaction amount.")
        try:
            database.save_request_log(request, False, "Non positive transaction amount.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.delayed_reply_invalid_value(request)
        return

    log.debug("Checking if user has enough credit.")
    try:
        if not database.user_has_enough_credit(request["user_id"], transaction_amount):
            log.info("User does not have enough credit.")
            try:
                database.save_request_log(request, False, "Not enough money.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.buy_delayed_reply_not_enough_money(request)
            return
    except exceptions.QueryDatabaseError:
        log.critical("Could not verify users balance: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform origin balance check.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return

    # Update both teams balances and register transaction
    log.debug("Do the transaction.")
    try:
        description = parse_transaction_description(request_args[2:])
        database.perform_buy(request["user_id"], destination_slack_user_id, transaction_amount, description)
    except exceptions.QueryDatabaseError as ex:
        log.critical("Failed to perform transaction: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform transaction.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
        return
    else:
        log.debug("Transaction done.")
        try:
            database.save_request_log(request, True, "Transaction succeeded.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.buy_delayed_reply_success(request, destination_slack_user_id)

def list_transactions_dispatcher(request):
    """Dispatcher to list transactions requests/commands."""
    log.debug("List transactions request.")

    # Check if quantity is valid
    request_args = get_request_args(request["text"])

    if not request_args:
        transactions_quantity = 10
    else:
        try:
            transactions_quantity = parse_transaction_quantity(request_args[0])
        except exceptions.IntegerParseError as ex:
            log.warn("Could not perform quantity parsing.")
            transactions_quantity = 10

    # Check if value is positive
    if transactions_quantity <= 0:
        log.error("Non positive transactions quantity.")
        try:
            database.save_request_log(request, False, "Non positive quantity provided.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.delayed_reply_invalid_value(request)
        return

    # Check if user is in a team
    log.debug("Checking if user is in a team.")
    try:
        if not database.user_has_team(request["user_id"]):
            # User has no team
            log.debug("User has no team.")
            responder.delayed_reply_no_team(request)
            try:
                database.save_request_log(request, False, "User has no team.")
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

    try:
        log.debug("Retrieving {} transactions from database.".format(transactions_quantity))
        transactions = database.get_last_transactions(request["user_id"], transactions_quantity)
    except exceptions.QueryDatabaseError as ex:
        log.critical("Transactions history lookup failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform transactions history check.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
    else:
        log.debug("Retrieved data.")
        try:
            database.save_request_log(request, True, "Transaction list collected.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.list_transactions_delayed_reply_success(request, transactions)

def list_teams_dispatcher(request):
    """Dispatcher to list teams requests/commands."""
    log.debug("List teams request.")
    # TODO: Change response to "No teams" if no teams were found.

    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        log.error("User has no permission to execute this command.")
        try:
            database.save_request_log(request, False, "Unauthorized.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.unauthorized_error(request)
        return

    try:
        log.debug("Getting teams")
        teams = database.get_teams()
        log.debug(teams)
    except exceptions.QueryDatabaseError as ex:
        log.critical("List teams search failed: {}".format(ex))
        responder.default_error()
        try:
            database.save_request_log(request, False, "Could not perform teams list search.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        return
    else:
        log.debug("Retrieved data.")
        try:
            database.save_request_log(request, True, "Team list collected.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.list_teams_delayed_reply_success(request, teams)

def list_teams_registration_dispatcher(request):
    """Dispatcher to list teams registrations requests/commands."""
    log.debug("List teams request.")
    # TODO: Change response to "No teams" if no teams were found.

    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        log.error("User has no permission to execute this command.")
        try:
            database.save_request_log(request, False, "Unauthorized.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.unauthorized_error(request)
        return

    try:
        log.debug("Getting teams registrations.")
        teams = database.get_teams_registration()
        log.debug(teams)
    except exceptions.QueryDatabaseError as ex:
        log.critical("List teams search failed: {}".format(ex))
        responder.default_error()
        try:
            database.save_request_log(request, False, "Could not perform registration teams list search.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        return
    else:
        log.debug("Retrieved data.")
        try:
            database.save_request_log(request, True, "Registration team list collected.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.list_teams_registration_delayed_reply_success(request, teams)

def team_details_dispatcher(request):
    """Dispatcher to team details requests/commands."""
    log.debug("Team details request.")

    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        log.error("User has no permission to execute this command.")
        try:
            database.save_request_log(request, False, "Unauthorized.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.unauthorized_error(request)
        return

    # Get team_id from args
    team_id = request["text"]
    if not team_id:
        # Bad usage
        log.warn("Bad format on command given.")
        responder.team_details_delayed_reply_bad_usage(request)
        try:
            database.save_request_log(request, False, "Not enough arguments.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        return

    try:
        log.debug("Getting team details.")
        details = database.get_team_details(team_id)
        log.debug(details)
        users = database.get_team_users(team_id)
        log.debug(users)
    except exceptions.QueryDatabaseError as ex:
        log.critical("Team details/users search failed: {}".format(ex))
        responder.default_error()
        try:
            database.save_request_log(request, False, "Could not fetch team details/users from the database.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        return
    else:
        log.debug("Retrieved data.")
        try:
            database.save_request_log(request, True, "Team details collected.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.team_details_delayed_reply_success(request, details, users)

def user_details_dispatcher(request):
    """Dispatcher to user details requests/commands."""
    log.debug("User details request.")

    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        log.error("User has no permission to execute this command.")
        try:
            database.save_request_log(request, False, "Unauthorized.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.unauthorized_error(request)
        return

    # Get user from args
    args = get_request_args(request["text"])
    if not args or len(args) > 1:
        # Bad usage
        log.warn("Bad format on command given.")
        responder.user_details_delayed_reply_bad_usage(request)
        try:
            database.save_request_log(request, False, "Not enough arguments.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        return

    user = args[0]
    user_id = get_slack_user_id_from_arg(user)
    if user_id:
        try:
            user_info = database.get_user_details_from_slack_id(user_id)
        except exceptions.QueryDatabaseError as ex:
            log.critical("User details search failed: {}".format(ex))
            try:
                database.save_request_log(request, False, "Could not fetch user details from the database.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.default_error()
            return
    elif check_valid_uuid4(user):
        try:
            user_info = database.get_user_details_from_user_id(user)
        except exceptions.QueryDatabaseError as ex:
            log.critical("User details search failed: {}".format(ex))
            try:
                database.save_request_log(request, False, "Could not fetch user details from the database.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.default_error()
            return
    else:
        log.debug("Both formats invalid.")
        try:
            database.save_request_log(request, False, "Invalid user_id/slack name.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.user_details_delayed_reply_bad_usage(request)
        return

    log.debug(user_info)
    try:
        database.save_request_log(request, True, "User details fetched.")
    except exceptions.SaveRequestLogError:
        log.error("Failed to save request log on database.")

    responder.user_details_delayed_reply_success(request, user_info)

def list_my_transactions_dispatcher(request):
    """Dispatcher to list my transactions requests/commands."""
    log.debug("List transactions request.")

    # Check if quantity is valid
    request_args = get_request_args(request["text"])

    if not request_args:
        transactions_quantity = 10
    else:
        try:
            transactions_quantity = parse_transaction_quantity(request_args[0])
        except exceptions.IntegerParseError as ex:
            log.warn("Could not perform quantity parsing.")
            transactions_quantity = 10

    # Check if value is positive
    if transactions_quantity <= 0:
        log.error("Non positive transactions quantity.")
        try:
            database.save_request_log(request, False, "Non positive quantity provided.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.delayed_reply_invalid_value(request)
        return

    # Check if user is in a team
    log.debug("Checking if user is in a team.")
    try:
        if not database.user_has_team(request["user_id"]):
            # User has no team
            log.debug("User has no team.")
            responder.delayed_reply_no_team(request)
            try:
                database.save_request_log(request, False, "User has no team.")
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

    try:
        log.debug("Retrieving {} transactions from database.".format(transactions_quantity))
        transactions = database.get_last_user_transactions(request["user_id"], transactions_quantity)
    except exceptions.QueryDatabaseError as ex:
        log.critical("User transactions history lookup failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not perform user transactions history check.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
    else:
        log.debug("Retrieved data.")
        try:
            database.save_request_log(request, True, "Transaction list collected.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.list_user_transactions_delayed_reply_success(request, transactions)

def change_permissions_dispatcher(request):
    """Dispatcher to change permissions requests/commands."""
    log.debug("Change permissions request.")

    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        log.error("User has no permission to execute this command.")
        try:
            database.save_request_log(request, False, "Unauthorized.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.unauthorized_error(request)
        return

    # Check if args are present
    request_args = get_request_args(request["text"])

    if not request_args or len(request_args) != 2:
        log.error("Bad usage of command.")
        try:
            database.save_request_log(request, False, "Bad argument format.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.change_permission_delayed_reply_bad_usage(request)
        return

    slack_user_id = get_slack_user_id_from_arg(request_args[0])
    if not slack_user_id:
        log.error("Bad usage of command: User not found")
        try:
            database.save_request_log(request, False, "Bad argument format on user.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.change_permission_delayed_reply_bad_usage(request)
        return

    new_permission = request_args[1]
    if not any(new_permission in x for x in ["admin", "staff", "remover"]):
        log.error("Bad usage of command: New role invalid.")
        try:
            database.save_request_log(request, False, "Bad argument format on new permission.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.change_permission_delayed_reply_bad_usage(request)
        return

    if new_permission == "remover":
        log.debug("Remove user from staff/admin")
        try:
            database.remove_user_permissions(slack_user_id)
        except exceptions.QueryDatabaseError as ex:
            log.critical("User permisions removal failed: {}".format(ex))
            try:
                database.save_request_log(request, False, "Could not remove user permissions.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.default_error()
    else:
        try:
            if database.user_is_staff(slack_user_id):
                log.debug("Update role.")
                try:
                    database.update_user_role(slack_user_id, new_permission)
                except exceptions.QueryDatabaseError as ex:
                    log.critical("User permisions update failed: {}".format(ex))
                    try:
                        database.save_request_log(request, False, "Could not update user permissions.")
                    except exceptions.SaveRequestLogError:
                        log.error("Failed to save request log on database.")
                    responder.default_error()
                else:
                    log.debug("User permisions updated.")
                    try:
                        database.save_request_log(request, True, "Updated user permissions.")
                    except exceptions.SaveRequestLogError:
                        log.error("Failed to save request log on database.")
                    responder.change_permission_delayed_reply_success(request)
            else:
                log.debug("Add to staff.")
                try:
                    database.add_user_to_staff(slack_user_id, new_permission)
                except exceptions.QueryDatabaseError as ex:
                    log.critical("User permisions update failed: {}".format(ex))
                    try:
                        database.save_request_log(request, False, "Could not update user permissions.")
                    except exceptions.SaveRequestLogError:
                        log.error("Failed to save request log on database.")
                    responder.default_error()
                else:
                    log.debug("User permisions updated.")
                    try:
                        database.save_request_log(request, True, "User added to staff.")
                    except exceptions.SaveRequestLogError:
                        log.error("Failed to save request log on database.")
                    responder.change_permission_delayed_reply_success(request)
        except exceptions.QueryDatabaseError as ex:
            log.critical("User permisions check failed: {}".format(ex))
            try:
                database.save_request_log(request, False, "Could not check user permissions.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.default_error()

def list_staff_dispatcher(request):
    """Dispatcher to list staff requests/commands."""
    log.debug("List staff request.")

    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        log.error("User has no permission to execute this command.")
        try:
            database.save_request_log(request, False, "Unauthorized.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.unauthorized_error(request)
        return

    try:
        staff_team = database.get_staff_team()
    except exceptions.QueryDatabaseError as ex:
        log.critical("Staff team lookup failed: {}".format(ex))
        try:
            database.save_request_log(request, False, "Could not get staff team.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.default_error()
    else:
        log.debug("Staf team retrieved.")
        try:
            database.save_request_log(request, True, "Staff team retrieved.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.list_staff_delayed_reply_success(request, staff_team)

def hackerboy_dispatcher(request):
    """Dispatcher to hackerboy requests/commands."""
    log.debug("List staff request.")

    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        log.error("User has no permission to execute this command.")
        try:
            database.save_request_log(request, False, "Unauthorized.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.unauthorized_error(request)
        return

    # Check if args are present
    request_args = get_request_args(request["text"])

    if not request_args or len(request_args) < 2:
        log.error("Bad usage of command.")
        try:
            database.save_request_log(request, False, "Bad argument format.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.hackerboy_delayed_reply_bad_usage(request)
        return

    # Parse value to change
    try:
        change_amount = parse_transaction_amount(request_args[0])
    except exceptions.FloatParseError as ex:
        log.critical("Failed to parse value to float.")
        try:
            database.save_request_log(request, False, "Could not perform amount value parsing.")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        responder.delayed_reply_invalid_value(request)
        return

    log.debug(change_amount)
    # Check if all teams will have a positive amount of money
    if change_amount > 0:
        # add money to all teams
        try:
            database.alter_money_to_all_teams(change_amount)
        except exceptions.QueryDatabaseError as ex:
            log.critical("Failed to add money to all teams: {}".format(ex))
            try:
                database.save_request_log(request, False, "Failed to add money to all teams.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.default_error()
        else:
            log.debug("Money on all teams updated.")
            try:
                description = parse_transaction_description(request_args[1:])
                database.save_reward(request, change_amount, description)
            except exceptions.QueryDatabaseError:
                log.error("Failed to save reward record.")
            try:
                database.save_request_log(request, True, "Balance updated.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.hackerboy_delayed_reply_success(request, change_amount)

    elif change_amount < 0:
        try:
            if database.all_teams_balance_above(abs(change_amount)):
                # Enough money on all teams
                try:
                    database.alter_money_to_all_teams(change_amount)
                except exceptions.QueryDatabaseError as ex:
                    log.critical("Balance update on teams failed: {}".format(ex))
                    try:
                        database.save_request_log(request, False, "Could not update teams balance.")
                    except exceptions.SaveRequestLogError:
                        log.error("Failed to save request log on database.")
                    responder.default_error()
                else:
                    log.debug("Money on all teams updated.")
                    try:
                        description = parse_transaction_description(request_args[1:])
                        database.save_reward(request, change_amount, description)
                    except exceptions.QueryDatabaseError:
                        log.error("Failed to save reward record.")
                    try:
                        database.save_request_log(request, True, "Balance updated.")
                    except exceptions.SaveRequestLogError:
                        log.error("Failed to save request log on database.")
                    responder.hackerboy_delayed_reply_success(request, change_amount)
            else:
                # Not all teams have enough
                log.debug("Not all teams have enough money.")
                try:
                    database.save_request_log(request, False, "Not enough money on some teams.")
                except exceptions.SaveRequestLogError:
                    log.error("Failed to save request log on database.")
                responder.hackerboy_delayed_reply_not_enough_money_on_some_teams(request, change_amount)
                return
        except exceptions.QueryDatabaseError as ex:
            log.critical("Balance check on teams failed: {}".format(ex))
            try:
                database.save_request_log(request, False, "Could not check teams balance.")
            except exceptions.SaveRequestLogError:
                log.error("Failed to save request log on database.")
            responder.default_error()
    else:
        log.debug("Hackerboy requested a balance update of 0.")
        try:
            database.save_request_log(request, True, "Balance updated (no change, value was 0).")
        except exceptions.SaveRequestLogError:
            log.error("Failed to save request log on database.")
        try:
            description = parse_transaction_description(request_args[1:])
            database.save_reward(request, change_amount, description)
        except exceptions.QueryDatabaseError:
            log.error("Failed to save reward record.")
        responder.hackerboy_delayed_reply_success(request, change_amount)

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

def get_request_args(args_str):
    return args_str.split()

def get_slack_user_id_from_arg(arg):
    regex = r"(?<=@)(.*?)(?=\|)"
    matches = re.search(regex, arg)
    if matches:
        return matches.group(1)
    else:
        log.warn("No match was found for user.")
        return None

def parse_transaction_amount(amount_str):
    try:
        return float(amount_str)
    except Exception as ex:
        log.critical("Can not parse transaction value to float: {}".format(ex))
        raise exceptions.FloatParseError("Failed to convert string to float.")

def parse_transaction_quantity(amount_str):
    try:
        return int(amount_str)
    except Exception as ex:
        log.critical("Can not parse transaction quantity to int: {}".format(ex))
        raise exceptions.IntegerParseError("Failed to convert string to int.")

def parse_transaction_description(description_list):
    return " ".join(description_list)

def check_valid_uuid4(arg):
    try:
        uuid.UUID(arg, version=4)
    except ValueError:
        log.warn("Invalid uuid4 format.")
        return False
    else:
        return True
