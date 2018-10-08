import logging as logger
import database
import responder
from threading import Thread
from queue import Queue
import definitions
import common
import exceptions
import uuid
import random
import string
import re
import uuid
import security
import slackapi
import log_messages as messages
import db_request_messages as db_messages


common.setup_logger()

requests_queue = Queue()

def start():
    """Starts a request dispatcher thread."""
    logger.debug(messages.DISPATCHER_STARTING)

    t = Thread(target=general_dispatcher, name="DispatcherThread")
    t.setDaemon(True)
    t.start()

def general_dispatcher():
    """Main dispatcher loop"""
    while True:
        request = requests_queue.get()
        logger.debug(messages.DISPATCH_REQUEST_STARTING)

        if request["command"] == definitions.SLACK_COMMANDS["CREATE_TEAM"]:
            create_team_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["JOIN_TEAM"]:
            join_team_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["CHECK_BALANCE"]:
            check_balance_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["BUY"]:
            buy_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["LIST_TRANSACTIONS"]:
            list_transactions_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["LIST_TEAMS"]:
            list_teams_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["LIST_TEAMS_REGISTRATION"]:
            list_teams_registration_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["TEAM_DETAILS"]:
            team_details_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["USER_DETAILS"]:
            user_details_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["LIST_MY_TRANSACTIONS"]:
            list_my_transactions_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["CHANGE_PERMISSIONS"]:
            change_permissions_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["LIST_STAFF"]:
            list_staff_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["HACKERBOY"]:
            hackerboy_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["HACKERBOY_TEAM"]:
            hackerboy_team_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["LIST_USER_TRANSACTIONS"]:
            list_user_transactions_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["LIST_TEAM_TRANSACTIONS"]:
            list_team_transactions_dispatcher(request)
        elif request["command"] == definitions.SLACK_COMMANDS["LIST_ALL_TRANSACTIONS"]:
            list_all_transactions_dispatcher(request)
        else:
            logger.error(messages.INVALID_REQUEST_COMMAND_VALUE)
            if not slackapi.logger_error(messages.INVALID_REQUEST_COMMAND_VALUE):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.INVALID_REQUEST_COMMAND_VALUE)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
        logger.debug(messages.DISPATCH_REQUEST_COMPLETE)
        requests_queue.task_done()

def create_team_dispatcher(request):
    """Dispatcher to create team requests/commands."""
    logger.info(messages.REQUEST_CREATE_TEAM_START)
    if not slackapi.logger_info(messages.REQUEST_CREATE_TEAM_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    team_name = request['text']
    if not team_name:
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.create_team_delayed_reply_missing_args(request)
        return

    try:
        if database.team_name_available(team_name):
            # Team name available
            team_entry_code = generate_team_entry_code()
            try:
                new_team_id = database.save_team_registration(team_name, team_entry_code)
            except exceptions.QueryDatabaseError as ex:
                logger.critical(messages.REGISTRATION_TEAM_SAVE_FAILED.format(ex))
                if not slackapi.logger_critical(messages.REGISTRATION_TEAM_SAVE_FAILED.format(ex)):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
                try:
                    database.save_request_log(request, False, db_messages.REGISTRATION_TEAM_SAVE_FAILED)
                except exceptions.SaveRequestLogError:
                    logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                responder.delayed_reply_default_error(request)
            else:
                try:
                    database.save_request_log(request, True, db_messages.REGISTRATION_TEAM_SAVE_SUCCESS)
                except exceptions.SaveRequestLogError:
                    logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                responder.create_team_delayed_reply_success(request, new_team_id, team_name, team_entry_code)
                return
        else:
            # Team name already picked
            logger.warn(messages.TEAM_NAME_EXISTS)
            if not slackapi.logger_warning(messages.TEAM_NAME_EXISTS):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.TEAM_NAME_EXISTS)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.create_team_delayed_reply_name_exists(request, team_name)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TEAM_NAME_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TEAM_NAME_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TEAM_NAME_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)

def join_team_dispatcher(request):
    """Dispatcher to join team requests/commands."""
    logger.info(messages.REQUEST_JOIN_TEAM_START)
    if not slackapi.logger_info(messages.REQUEST_JOIN_TEAM_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    team_name = request['text']
    if not team_name:
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.create_team_delayed_reply_missing_args(request)
        return

    team_entry_code = request["text"]
    if not team_entry_code:
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.join_team_delayed_reply_missing_args(request)
        return

    # Check if user has a team
    try:
        if database.user_has_team(request["user_id"]):
            # User already on team.
            logger.warn(messages.USER_ALREADY_ON_TEAM)
            try:
                database.save_request_log(request, False, db_messages.USER_ALREADY_ON_TEAM)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.join_team_delayed_reply_already_on_team(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_HAS_TEAM_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    # Check if provided code is valid
    team_info = {}
    try:
        team_info = database.valid_entry_code(team_entry_code)
        if not team_info:
            logger.warn(messages.INVALID_ENTRY_CODE)
            if not slackapi.logger_warning(messages.INVALID_ENTRY_CODE):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.INVALID_ENTRY_CODE)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.join_team_delayed_reply_invalid_code(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.ENTRY_CODE_VALIDATION_FAILED.format(ex))
        if not slackapi.logger_critical(messages.ENTRY_CODE_VALIDATION_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.ENTRY_CODE_VALIDATION_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    try:
        # Check if team already created.
        if not database.is_team_created(team_info["id"]):
            # Create new team and private channel
            slack_group_results = slackapi.create_group(definitions.TEAM_CHANNEL_PREFIX + team_info["name"])
            if not slack_group_results:
                # Error creating group
                logger.error(messages.TEAM_CHANNEL_NOT_CREATED.format(slack_group_results[1]))
                if not slackapi.logger_error(messages.TEAM_CHANNEL_NOT_CREATED.format(slack_group_results[1])):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
                team_info["channel_id"] = None
                # NOTE: Team will be created without a private channel. Proceed?
            else:
                team_info["channel_id"] = slack_group_results[1][0]
            try:
                database.create_team(team_info)
            except exceptions.QueryDatabaseError as ex:
                logger.critical(messages.TEAM_CREATION_FAILED.format(ex))
                if not slackapi.logger_error(messages.TEAM_CREATION_FAILED.format(ex)):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
                try:
                    database.save_request_log(request, False, db_messages.TEAM_CREATION_FAILED)
                except exceptions.SaveRequestLogError:
                    logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                responder.delayed_reply_default_error(request)
                return
        else:
            # Team was already created, get channel id from the database
            try:
                team_info["channel_id"] = database.get_team_slack_group_id(team_info["id"])
                # NOTE: If the fetch fails, the process continues
            except exceptions.QueryDatabaseError as ex:
                logger.error(messages.TEAM_CHANNEL_NOT_CREATED.format(ex))
                if not slackapi.logger_error(messages.TEAM_CHANNEL_NOT_CREATED.format(ex)):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TEAM_SEARCH_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TEAM_SEARCH_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TEAM_SEARCH_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    if not slackapi.invite_to_group(team_info["channel_id"], request["user_id"]):
        logger.error(messages.ADD_USER_TO_TEAM_CHANNEL_FAILED)
        if not slackapi.logger_error(messages.ADD_USER_TO_TEAM_CHANNEL_FAILED):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
    try:
        database.add_user_to_team(request["user_id"], team_info["id"])
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.ADD_USER_TO_TEAM_FAILED.format(ex))
        if not slackapi.logger_critical(messages.ADD_USER_TO_TEAM_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.ADD_USER_TO_TEAM_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
    else:
        try:
            database.save_request_log(request, True, db_messages.JOIN_TEAM_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.join_team_delayed_reply_success(request, team_info["name"])

def check_balance_dispatcher(request):
    """Dispatcher to check balance requests/commands."""
    logger.info(messages.REQUEST_CHECK_BALANCE_START)
    if not slackapi.logger_info(messages.REQUEST_CHECK_BALANCE_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # First, check if user is in a team
    try:
        if not database.user_has_team(request["user_id"]):
            logger.warn(messages.USER_WITHOUT_TEAM)
            if not slackapi.logger_warning(messages.USER_WITHOUT_TEAM):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.USER_WITHOUT_TEAM)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.check_balance_delayed_reply_no_team(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_HAS_TEAM_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    # If has a team, get the team balance
    try:
        [team_name, team_balance] = database.get_users_balance(request["user_id"])
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_BALANCE_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_BALANCE_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_BALANCE_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.CHECK_BALANCE_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.check_balance_delayed_reply_success(request, team_name, team_balance)

def buy_dispatcher(request):
    """Dispatcher to buy requests/commands."""
    logger.info(messages.REQUEST_BUY_START)
    if not slackapi.logger_info(messages.REQUEST_BUY_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Check if args are present
    request_args = get_request_args(request["text"])
    if not request_args or len(request_args) < 3:
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.buy_delayed_reply_missing_args(request)
        return

    # Check if user is in a team
    try:
        if not database.user_has_team(request["user_id"]):
            # User has no team
            logger.warn(messages.USER_WITHOUT_TEAM)
            if not slackapi.logger_warning(messages.USER_WITHOUT_TEAM):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.USER_WITHOUT_TEAM)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.buy_delayed_reply_no_team(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_HAS_TEAM_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    # User has a team
    destination_slack_user_id = get_slack_user_id_from_arg(request_args[0])
    if not destination_slack_user_id:
        logger.warn(messages.ARG_NO_DESTINATION_USER)
        if not slackapi.logger_warning(messages.ARG_NO_DESTINATION_USER):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.ARG_NO_DESTINATION_USER)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.buy_delayed_reply_no_user_arg(request)
        return

    # Check if destination is valid (exists and has a team, not the same user and not in the same team)
    if request["user_id"] == destination_slack_user_id:
        logger.info(messages.DESTINATION_ORIGIN_USER_SAME)
        if not slackapi.logger_info(messages.DESTINATION_ORIGIN_USER_SAME):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.DESTINATION_ORIGIN_USER_SAME)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.buy_delayed_reply_destination_himself(request)
        return

    try:
        if not database.user_has_team(destination_slack_user_id):
            logger.info(messages.DESTINATION_USER_WITHOUT_TEAM)
            if not slackapi.logger_info(messages.DESTINATION_USER_WITHOUT_TEAM):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.DESTINATION_USER_WITHOUT_TEAM)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.buy_delayed_reply_destination_no_team(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_HAS_TEAM_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    # Check if origin and destination teams are different
    try:
        if not database.users_with_different_team(destination_slack_user_id, request["user_id"]):
            logger.info(messages.DESTINATION_ORIGIN_SAME_TEAM)
            if not slackapi.logger_info(messages.DESTINATION_ORIGIN_SAME_TEAM):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.DESTINATION_ORIGIN_SAME_TEAM)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.buy_delayed_reply_destination_same_team(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.DESTINATION_ORIGIN_TEAMS_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.DESTINATION_ORIGIN_TEAMS_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.DESTINATION_ORIGIN_TEAMS_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    # Parse transaction value
    try:
        transaction_amount = parse_transaction_amount(request_args[1])
    except exceptions.FloatParseError as ex:
        logger.critical(messages.TRANSACTION_AMOUNT_PARSING_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TRANSACTION_AMOUNT_PARSING_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TRANSACTION_AMOUNT_PARSING_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_invalid_value(request)
        return

    # Check if value is positive
    if transaction_amount <= 0:
        logger.info(messages.BUY_NON_POSITIVE_AMOUNT)
        if not slackapi.logger_info(messages.BUY_NON_POSITIVE_AMOUNT):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.BUY_NON_POSITIVE_AMOUNT)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_invalid_value(request)
        return

    # Check if user has enough credit.
    try:
        if not database.user_has_enough_credit(request["user_id"], transaction_amount):
            logger.info(messages.NOT_ENOUGH_CREDIT)
            if not slackapi.logger_info(messages.NOT_ENOUGH_CREDIT):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.NOT_ENOUGH_CREDIT)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.buy_delayed_reply_not_enough_money(request)
            return
    except exceptions.QueryDatabaseError:
        logger.critical(messages.USER_BALANCE_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_BALANCE_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_BALANCE_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    # Update both teams balances and register transaction
    try:
        description = parse_transaction_description(request_args[2:])
        database.perform_buy(request["user_id"], destination_slack_user_id, transaction_amount, description)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.BUY_OPERATION_FAILED.format(ex))
        if not slackapi.logger_critical(messages.BUY_OPERATION_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.BUY_OPERATION_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        # Transaction done.
        try:
            channel_id = database.get_team_slack_group_id_from_slack_user_id(destination_slack_user_id)
        except exceptions.QueryDatabaseError as ex:
            logger.error(messages.TEAM_CHANNEL_LOOKUP_FAILED.format(ex))
            if not slackapi.logger_error(messages.TEAM_CHANNEL_LOOKUP_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
        else:
            # Post message on destination team channel, if found
            if channel_id:
                if not slackapi.post_transaction_received_message(channel_id, transaction_amount, request["user_id"]):
                    logger.warn(messages.SLACK_POST_TRANSACTION_FAILED)
                    if not slackapi.logger_warning(messages.SLACK_POST_TRANSACTION_FAILED):
                        logger.warn(messages.SLACK_POST_LOG_FAILED)
            else:
                logger.warn(messages.TEAM_CHANNEL_NOT_FOUND)
                if not slackapi.logger_warning(messages.TEAM_CHANNEL_NOT_FOUND):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, True, db_messages.BUY_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.buy_delayed_reply_success(request, destination_slack_user_id)

def list_transactions_dispatcher(request):
    """Dispatcher to list transactions requests/commands."""
    logger.info(messages.REQUEST_LIST_TRANSACTIONS_START)
    if not slackapi.logger_info(messages.REQUEST_LIST_TRANSACTIONS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Check if quantity is valid
    request_args = get_request_args(request["text"])
    if not request_args:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH
    else:
        try:
            transactions_quantity = parse_transaction_quantity(request_args[0])
        except exceptions.IntegerParseError:
            transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

    # Check if value is positive
    if transactions_quantity <= 0:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

    # Check if value is not above the max
    if transactions_quantity > definitions.DATABASE_MAX_LIMIT:
        transactions_quantity = definitions.DATABASE_MAX_LIMIT

    # Check if user is in a team
    try:
        if not database.user_has_team(request["user_id"]):
            # User has no team
            logger.warn(messages.USER_WITHOUT_TEAM)
            if not slackapi.logger_warning(messages.USER_WITHOUT_TEAM):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.USER_WITHOUT_TEAM)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.list_transactions_delayed_reply_no_team(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_HAS_TEAM_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    try:
        # Retrieve 'transaction_quantity' transactions from the database.
        transactions = database.get_last_transactions(request["user_id"], transactions_quantity)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TRANSACTIONS_LIST_SEARCH_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.LIST_TRANSACTIONS_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_transactions_delayed_reply_success(request, transactions)

def list_teams_dispatcher(request):
    """Dispatcher to list teams requests/commands."""
    logger.info(messages.REQUEST_LIST_TEAMS_START)
    if not slackapi.logger_info(messages.REQUEST_LIST_TEAMS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    try:
        teams = database.get_teams()
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TEAM_LIST_RETRIEVE_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TEAM_LIST_RETRIEVE_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TEAM_LIST_RETRIEVE_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.TEAM_LIST_RETRIEVE_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_teams_delayed_reply_success(request, teams)

def list_teams_registration_dispatcher(request):
    """Dispatcher to list teams registrations requests/commands."""
    logger.info(messages.REQUEST_LIST_REGISTRATION_TEAMS_START)
    if not slackapi.logger_info(messages.REQUEST_LIST_REGISTRATION_TEAMS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    try:
        teams = database.get_teams_registration()
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.REGISTRATION_TEAM_LIST_RETRIEVE_FAILED.format(ex))
        if not slackapi.logger_critical(messages.REGISTRATION_TEAM_LIST_RETRIEVE_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.REGISTRATION_TEAM_LIST_RETRIEVE_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.REGISTRATION_TEAM_LIST_RETRIEVE_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_teams_registration_delayed_reply_success(request, teams)

def team_details_dispatcher(request):
    """Dispatcher to team details requests/commands."""
    logger.info(messages.REQUEST_TEAM_DETAILS_START)
    if not slackapi.logger_info(messages.REQUEST_TEAM_DETAILS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    # Get team_id from args
    team_id = request["text"]
    if not team_id:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.team_details_delayed_reply_missing_args(request)
        return

    if not check_valid_uuid4(team_id):
        # Invalid team id
        logger.warn(messages.INVALID_UUID)
        if not slackapi.logger_warning(messages.INVALID_UUID):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.INVALID_UUID)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_argument_formating_error(request)
        return

    try:
        details = database.get_team_details(team_id)
        users = database.get_team_users(team_id)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TEAM_DETAILS_RETRIEVE_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TEAM_DETAILS_RETRIEVE_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TEAM_DETAILS_RETRIEVE_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.TEAM_DETAILS_RETRIEVE_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.team_details_delayed_reply_success(request, details, users)

def user_details_dispatcher(request):
    """Dispatcher to user details requests/commands."""
    logger.info(messages.REQUEST_USER_DETAILS_START)
    if not slackapi.logger_info(messages.REQUEST_USER_DETAILS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    # Get user from args
    args = get_request_args(request["text"])
    if not args or len(args) > 1:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.user_details_delayed_reply_missing_args(request)
        return

    user = args[0]
    user_id = get_slack_user_id_from_arg(user)
    if user_id:
        try:
            user_info = database.get_user_details_from_slack_id(user_id)
        except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.USER_SEARCH_FAILED.format(ex))
            if not slackapi.logger_critical(messages.USER_SEARCH_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.USER_SEARCH_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return
    elif check_valid_uuid4(user):
        try:
            user_info = database.get_user_details_from_user_id(user)
        except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.USER_SEARCH_FAILED.format(ex))
            if not slackapi.logger_critical(messages.USER_SEARCH_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.USER_SEARCH_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return
    else:
        logger.info(messages.BAD_USERNAME_FORMAT)
        if not slackapi.logger_info(messages.BAD_USERNAME_FORMAT):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.BAD_USERNAME_FORMAT)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.user_details_delayed_reply_missing_args(request)
        return

    try:
        database.save_request_log(request, True, db_messages.USER_DETAILS_RETRIEVE_SUCCESS)
    except exceptions.SaveRequestLogError:
        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
    responder.user_details_delayed_reply_success(request, user_info)

def list_my_transactions_dispatcher(request):
    """Dispatcher to list my transactions requests/commands."""
    logger.info(messages.REQUEST_LIST_MY_TRANSACTIONS_START)
    if not slackapi.logger_info(messages.REQUEST_LIST_MY_TRANSACTIONS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Check if quantity is valid
    request_args = get_request_args(request["text"])
    if not request_args:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH
    else:
        try:
            transactions_quantity = parse_transaction_quantity(request_args[0])
        except exceptions.IntegerParseError:
            transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

    # Check if value is positive
    if transactions_quantity <= 0:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

    # Check if value is not above the max
    if transactions_quantity > definitions.DATABASE_MAX_LIMIT:
        transactions_quantity = definitions.DATABASE_MAX_LIMIT

    # Check if user is in a team
    try:
        if not database.user_has_team(request["user_id"]):
            # User has no team
            logger.warn(messages.USER_WITHOUT_TEAM)
            if not slackapi.logger_warning(messages.USER_WITHOUT_TEAM):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.USER_WITHOUT_TEAM)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            # Same method as before works well
            responder.list_transactions_delayed_reply_no_team(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_HAS_TEAM_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    try:
        # Retrieve 'transaction_quantity' transactions from the database.
        transactions = database.get_last_user_transactions(request["user_id"], transactions_quantity)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TRANSACTIONS_LIST_SEARCH_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.LIST_TRANSACTIONS_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_user_transactions_delayed_reply_success(request, transactions)

def change_permissions_dispatcher(request):
    """Dispatcher to change permissions requests/commands."""
    logger.info(messages.REQUEST_CHANGE_PERMISSIONS_START)
    if not slackapi.logger_info(messages.REQUEST_CHANGE_PERMISSIONS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    # Check if args are present
    request_args = get_request_args(request["text"])
    if not request_args or len(request_args) != 2:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.change_permission_delayed_reply_missing_args(request)
        return

    slack_user_id = get_slack_user_id_from_arg(request_args[0])
    if not slack_user_id:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.change_permission_delayed_reply_missing_args(request)
        return

    new_permission = request_args[1]
    if not any(new_permission in x for x in ["admin", "staff", "remover"]):
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.change_permission_delayed_reply_missing_args(request)
        return

    if new_permission == "remover":
        try:
            database.remove_user_permissions(slack_user_id)
        except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.UPDATE_USER_PERMISSIONS_FAILED.format(ex))
            if not slackapi.logger_critical(messages.UPDATE_USER_PERMISSIONS_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.UPDATE_USER_PERMISSIONS_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return
        else:
            try:
                database.save_request_log(request, True, db_messages.UPDATE_USER_PERMISSONS_SUCCESS)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.change_permission_delayed_reply_success(request)
    else:
        try:
            if database.user_is_staff(slack_user_id):
                # Update role
                try:
                    database.update_user_role(slack_user_id, new_permission)
                except exceptions.QueryDatabaseError as ex:
                    logger.critical(messages.UPDATE_USER_PERMISSIONS_FAILED.format(ex))
                    if not slackapi.logger_critical(messages.UPDATE_USER_PERMISSIONS_FAILED.format(ex)):
                        logger.warn(messages.SLACK_POST_LOG_FAILED)
                    try:
                        database.save_request_log(request, False, db_messages.UPDATE_USER_PERMISSIONS_FAILED)
                    except exceptions.SaveRequestLogError:
                        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                    responder.delayed_reply_default_error(request)
                    return
                else:
                    try:
                        database.save_request_log(request, True, db_messages.UPDATE_USER_PERMISSONS_SUCCESS)
                    except exceptions.SaveRequestLogError:
                        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                    responder.change_permission_delayed_reply_success(request)
            else:
                # Add to staff
                try:
                    database.add_user_to_staff(slack_user_id, new_permission)
                except exceptions.QueryDatabaseError as ex:
                    logger.critical(messages.UPDATE_USER_PERMISSIONS_FAILED.format(ex))
                    if not slackapi.logger_critical(messages.UPDATE_USER_PERMISSIONS_FAILED.format(ex)):
                        logger.warn(messages.SLACK_POST_LOG_FAILED)
                    try:
                        database.save_request_log(request, False, db_messages.UPDATE_USER_PERMISSIONS_FAILED)
                    except exceptions.SaveRequestLogError:
                        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                    responder.delayed_reply_default_error(request)
                    return
                else:
                    try:
                        database.save_request_log(request, True, db_messages.UPDATE_USER_PERMISSONS_SUCCESS)
                    except exceptions.SaveRequestLogError:
                        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                    responder.change_permission_delayed_reply_success(request)
        except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.UPDATE_USER_PERMISSIONS_FAILED.format(ex))
            if not slackapi.logger_critical(messages.UPDATE_USER_PERMISSIONS_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.UPDATE_USER_PERMISSIONS_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return

def list_staff_dispatcher(request):
    """Dispatcher to list staff requests/commands."""
    logger.info(messages.REQUEST_LIST_STAFF_START)
    if not slackapi.logger_info(messages.REQUEST_LIST_STAFF_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Staff, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    try:
        staff_team = database.get_staff_team()
    except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.STAFF_TEAM_RETRIEVE_FAILED.format(ex))
            if not slackapi.logger_critical(messages.STAFF_TEAM_RETRIEVE_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.STAFF_TEAM_RETRIEVE_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return
    else:
        try:
            database.save_request_log(request, True, db_messages.STAFF_TEAM_RETRIEVE_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_staff_delayed_reply_success(request, staff_team)

def hackerboy_dispatcher(request):
    """Dispatcher to hackerboy requests/commands."""
    logger.info(messages.REQUEST_HACKERBOY_START)
    if not slackapi.logger_info(messages.REQUEST_HACKERBOY_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    # Check if args are present
    request_args = get_request_args(request["text"])
    if not request_args or len(request_args) < 2:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.hackerboy_delayed_reply_missing_args(request)
        return

    # Parse value to change
    try:
        change_amount = parse_transaction_amount(request_args[0])
    except exceptions.FloatParseError as ex:
        logger.error(messages.PARSING_INVALID_VALUE.format(ex))
        if not slackapi.logger_warning(messages.PARSING_INVALID_VALUE.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.PARSING_INVALID_VALUE)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_invalid_value(request)
        return

    if change_amount > 0:
        # add money to all teams
        try:
            database.alter_money_to_all_teams(change_amount)
        except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.UPDATE_TEAMS_BALANCE_FAILED.format(ex))
            if not slackapi.logger_critical(messages.UPDATE_TEAMS_BALANCE_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.UPDATE_TEAMS_BALANCE_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return
        else:
            # Money on all teams updated
            try:
                description = parse_transaction_description(request_args[1:])
                database.save_reward(request, change_amount, description)
            except exceptions.QueryDatabaseError as ex:
                # Proceed, just won't be recorded on the database
                logger.warn(messages.REWARD_LOG_FAILED.format(ex))
                if not slackapi.logger_warning(messages.REWARD_LOG_FAILED.format(ex)):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, True, db_messages.UPDATE_TEAMS_BALANCE_SUCCESS)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            try:
                teams_channels_id = database.get_all_teams_slack_group_id()
            except exceptions.QueryDatabaseError as ex:
                logger.warn(messages.GET_TEAMS_CHANNEL_ID_FAILED.format(ex))
                if not slackapi.logger_warning(messages.GET_TEAMS_CHANNEL_ID_FAILED.format(ex)):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
            else:
                if not slackapi.post_hackerboy_action_general(teams_channels_id, change_amount, description):
                    logger.warn(messages.SLACK_POST_HACKERBOY_FAILED)
                    if not slackapi.logger_warning(messages.SLACK_POST_HACKERBOY_FAILED):
                        logger.warn(messages.SLACK_POST_LOG_FAILED)
            responder.hackerboy_delayed_reply_success(request, change_amount)
            return

    elif change_amount < 0:
        # Check if all teams will have a positive amount of money
        try:
            if database.all_teams_balance_above(abs(change_amount)):
                # Enough money on all teams
                try:
                    database.alter_money_to_all_teams(change_amount)
                except exceptions.QueryDatabaseError as ex:
                    logger.critical(messages.UPDATE_TEAMS_BALANCE_FAILED.format(ex))
                    if not slackapi.logger_critical(messages.UPDATE_TEAMS_BALANCE_FAILED.format(ex)):
                        logger.warn(messages.SLACK_POST_LOG_FAILED)
                    try:
                        database.save_request_log(request, False, db_messages.UPDATE_TEAMS_BALANCE_FAILED)
                    except exceptions.SaveRequestLogError:
                        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                    responder.delayed_reply_default_error(request)
                    return
                else:
                    # Money on all teams updated
                    try:
                        description = parse_transaction_description(request_args[1:])
                        database.save_reward(request, change_amount, description)
                    except exceptions.QueryDatabaseError:
                        # Proceed, just won't be recorded on the database
                        logger.warn(messages.REWARD_LOG_FAILED.format(ex))
                        if not slackapi.logger_warning(messages.REWARD_LOG_FAILED.format(ex)):
                            logger.warn(messages.SLACK_POST_LOG_FAILED)
                    try:
                        database.save_request_log(request, True, db_messages.UPDATE_TEAMS_BALANCE_SUCCESS)
                    except exceptions.SaveRequestLogError:
                        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                    try:
                        teams_channels_id = database.get_all_teams_slack_group_id()
                    except exceptions.QueryDatabaseError as ex:
                        logger.warn(messages.GET_TEAMS_CHANNEL_ID_FAILED.format(ex))
                        if not slackapi.logger_warning(messages.GET_TEAMS_CHANNEL_ID_FAILED.format(ex)):
                            logger.warn(messages.SLACK_POST_LOG_FAILED)
                    else:
                        if not slackapi.post_hackerboy_action_general(teams_channels_id, change_amount, description):
                            logger.warn(messages.SLACK_POST_HACKERBOY_FAILED)
                            if not slackapi.logger_warning(messages.SLACK_POST_HACKERBOY_FAILED):
                                logger.warn(messages.SLACK_POST_LOG_FAILED)
                    responder.hackerboy_delayed_reply_success(request, change_amount)
                    return
            else:
                # Not all teams have enough
                logger.warn(messages.HACKERBOY_NOT_ENOUGH_MONEY)
                if not slackapi.logger_warning(messages.HACKERBOY_NOT_ENOUGH_MONEY):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
                try:
                    database.save_request_log(request, False, db_messages.HACKERBOY_NOT_ENOUGH_MONEY)
                except exceptions.SaveRequestLogError:
                    logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                responder.hackerboy_delayed_reply_not_enough_money_on_some_teams(request, change_amount)
                return
        except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.HACKERBOY_BALANCE_CHECK_FAILED.format(ex))
            if not slackapi.logger_critical(messages.HACKERBOY_BALANCE_CHECK_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.HACKERBOY_BALANCE_CHECK_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return
    else:
        # Update of zero
        try:
            database.save_request_log(request, True, db_messages.UPDATE_TEAMS_BALANCE_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        try:
            description = parse_transaction_description(request_args[1:])
            database.save_reward(request, change_amount, description)
        except exceptions.QueryDatabaseError:
            # Proceed, just won't be recorded on the database
            logger.warn(messages.REWARD_LOG_FAILED.format(ex))
            if not slackapi.logger_warning(messages.REWARD_LOG_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
        responder.hackerboy_delayed_reply_success(request, change_amount)

def hackerboy_team_dispatcher(request):
    """Dispatcher to hackerboy team requests/commands."""
    logger.info(messages.REQUEST_HACKERBOY_TEAM_START)
    if not slackapi.logger_info(messages.REQUEST_HACKERBOY_TEAM_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    # Check if args are present
    request_args = get_request_args(request["text"])

    if not request_args or len(request_args) < 3:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.hackerboy_team_delayed_reply_missing_args(request)
        return

    # Check if valid team uuid
    team_id = request_args[0]
    if not check_valid_uuid4(team_id):
        # Invalid team id
        logger.warn(messages.INVALID_UUID)
        if not slackapi.logger_warning(messages.INVALID_UUID):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.INVALID_UUID)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_argument_formating_error(request)
        return

    # Parse value to change
    try:
        change_amount = parse_transaction_amount(request_args[1])
    except exceptions.FloatParseError as ex:
        logger.error(messages.PARSING_INVALID_VALUE.format(ex))
        if not slackapi.logger_warning(messages.PARSING_INVALID_VALUE.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.PARSING_INVALID_VALUE)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_invalid_value(request)
        return

    if change_amount > 0:
        # add money to team
        try:
            database.alter_money_to_team(team_id, change_amount)
        except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.UPDATE_TEAM_BALANCE_FAILED.format(ex))
            if not slackapi.logger_critical(messages.UPDATE_TEAM_BALANCE_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.UPDATE_TEAM_BALANCE_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return
        else:
            # Money on team updated
            try:
                description = parse_transaction_description(request_args[2:])
                database.save_reward_team(request, team_id, change_amount, description)
            except exceptions.QueryDatabaseError:
                # Proceed, just won't be recorded on the database
                logger.warn(messages.REWARD_LOG_FAILED.format(ex))
                if not slackapi.logger_warning(messages.REWARD_LOG_FAILED.format(ex)):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, True, db_messages.UPDATE_TEAM_BALANCE_SUCCESS)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            try:
                team_channel_id = database.get_team_slack_group_id(team_id)
            except exceptions.QueryDatabaseError as ex:
                logger.warn(messages.GET_TEAM_CHANNEL_ID_FAILED.format(ex))
                if not slackapi.logger_warning(messages.GET_TEAM_CHANNEL_ID_FAILED.format(ex)):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
            else:
                if not slackapi.post_hackerboy_action_team(team_channel_id, change_amount, description):
                    logger.warn(messages.SLACK_POST_HACKERBOY_TEAM_FAILED)
                    if not slackapi.logger_warning(messages.SLACK_POST_HACKERBOY_TEAM_FAILED):
                        logger.warn(messages.SLACK_POST_LOG_FAILED)

            responder.hackerboy_team_delayed_reply_success(request, change_amount)
            return
    elif change_amount < 0:
        try:
            if database.team_balance_above(team_id, abs(change_amount)):
                # Enough money on team
                try:
                    database.alter_money_to_team(team_id, change_amount)
                except exceptions.QueryDatabaseError as ex:
                    logger.critical(messages.UPDATE_TEAM_BALANCE_FAILED.format(ex))
                    if not slackapi.logger_critical(messages.UPDATE_TEAM_BALANCE_FAILED.format(ex)):
                        logger.warn(messages.SLACK_POST_LOG_FAILED)
                    try:
                        database.save_request_log(request, False, db_messages.UPDATE_TEAM_BALANCE_FAILED)
                    except exceptions.SaveRequestLogError:
                        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                    responder.delayed_reply_default_error(request)
                    return
                else:
                    # Money on team updated"
                    try:
                        description = parse_transaction_description(request_args[2:])
                        database.save_reward_team(request, team_id, change_amount, description)
                    except exceptions.QueryDatabaseError:
                        # Proceed, just won't be recorded on the database
                        logger.warn(messages.REWARD_LOG_FAILED.format(ex))
                        if not slackapi.logger_warning(messages.REWARD_LOG_FAILED.format(ex)):
                            logger.warn(messages.SLACK_POST_LOG_FAILED)
                    try:
                        database.save_request_log(request, True, db_messages.UPDATE_TEAM_BALANCE_SUCCESS)
                    except exceptions.SaveRequestLogError:
                        logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                    try:
                        team_channel_id = database.get_team_slack_group_id(team_id)
                    except exceptions.QueryDatabaseError as ex:
                        logger.warn(messages.GET_TEAM_CHANNEL_ID_FAILED.format(ex))
                        if not slackapi.logger_warning(messages.GET_TEAM_CHANNEL_ID_FAILED.format(ex)):
                            logger.warn(messages.SLACK_POST_LOG_FAILED)
                    else:
                        if not slackapi.post_hackerboy_action_team(team_channel_id, change_amount, description):
                            logger.warn(messages.SLACK_POST_HACKERBOY_TEAM_FAILED)
                            if not slackapi.logger_warning(messages.SLACK_POST_HACKERBOY_TEAM_FAILED):
                                logger.warn(messages.SLACK_POST_LOG_FAILED)
                    responder.hackerboy_team_delayed_reply_success(request, change_amount)
                    return
            else:
                logger.warn(messages.HACKERBOY_TEAM_NOT_ENOUGH_MONEY)
                if not slackapi.logger_warning(messages.HACKERBOY_TEAM_NOT_ENOUGH_MONEY):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
                try:
                    database.save_request_log(request, False, db_messages.HACKERBOY_TEAM_NOT_ENOUGH_MONEY)
                except exceptions.SaveRequestLogError:
                    logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                responder.hackerboy_team_delayed_reply_not_enough_money(request, change_amount)
                return
        except exceptions.QueryDatabaseError as ex:
            logger.critical(messages.HACKERBOY_TEAM_BALANCE_CHECK_FAILED.format(ex))
            if not slackapi.logger_critical(messages.HACKERBOY_TEAM_BALANCE_CHECK_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.HACKERBOY_TEAM_BALANCE_CHECK_FAILED)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_default_error(request)
            return
    else:
        # Update of zero
        try:
            database.save_request_log(request, True, db_messages.UPDATE_TEAM_BALANCE_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        try:
            description = parse_transaction_description(request_args[2:])
            database.save_reward(request, change_amount, description)
        except exceptions.QueryDatabaseError:
            # Proceed, just won't be recorded on the database
            logger.warn(messages.REWARD_LOG_FAILED.format(ex))
            if not slackapi.logger_warning(messages.REWARD_LOG_FAILED.format(ex)):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
        responder.hackerboy_team_delayed_reply_success(request, change_amount)

def list_user_transactions_dispatcher(request):
    """Dispatcher to list an user transactions requests/commands."""
    logger.info(messages.REQUEST_LIST_USER_TRANSACTIONS_START)
    if not slackapi.logger_info(messages.REQUEST_LIST_USER_TRANSACTIONS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    # Check if arguments are good
    request_args = get_request_args(request["text"])
    if not request_args or len(request_args) < 2:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_user_transactions_delayed_reply_missing_args(request)
        return

    slack_user_id = get_slack_user_id_from_arg(request_args[0])
    if not slack_user_id:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_user_transactions_delayed_reply_missing_args(request)
        return

    try:
        transactions_quantity = parse_transaction_quantity(request_args[1])
    except exceptions.IntegerParseError as ex:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

    if transactions_quantity <= 0:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

   # Check if value is not above the max
    if transactions_quantity > definitions.DATABASE_MAX_LIMIT:
        transactions_quantity = definitions.DATABASE_MAX_LIMIT

    # Check if user is in a team
    try:
        if not database.user_has_team(slack_user_id):
            # User has no team
            logger.warn(messages.USER_WITHOUT_TEAM)
            if not slackapi.logger_warning(messages.USER_WITHOUT_TEAM):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.USER_WITHOUT_TEAM)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.delayed_reply_user_has_no_team(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_HAS_TEAM_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_HAS_TEAM_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    try:
        # Retrieving 'transactions_quantity' transactions from the database
        transactions = database.get_last_user_transactions(slack_user_id, transactions_quantity)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TRANSACTIONS_LIST_SEARCH_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.LIST_TRANSACTIONS_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_to_admin_user_transactions_delayed_reply_success(request, transactions)

def list_team_transactions_dispatcher(request):
    """Dispatcher to list a team transactions requests/commands."""
    logger.info(messages.REQUEST_LIST_TEAM_TRANSACTIONS_START)
    if not slackapi.logger_info(messages.REQUEST_LIST_TEAM_TRANSACTIONS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    # Check if arguments are good
    request_args = get_request_args(request["text"])
    if not request_args or len(request_args) < 2:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_team_transactions_delayed_reply_missing_args(request)
        return

    team_id = request_args[0]
    if not check_valid_uuid4(team_id):
        # Invalid team id
        logger.warn(messages.INVALID_UUID)
        if not slackapi.logger_warning(messages.INVALID_UUID):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.INVALID_UUID)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_argument_formating_error(request)
        return

    try:
        transactions_quantity = parse_transaction_quantity(request_args[1])
    except exceptions.IntegerParseError as ex:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

    if transactions_quantity <= 0:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

   # Check if value is not above the max
    if transactions_quantity > definitions.DATABASE_MAX_LIMIT:
        transactions_quantity = definitions.DATABASE_MAX_LIMIT

    # Check if team exists
    try:
        if not database.is_team_created(team_id):
            logger.warn(messages.TEAM_NOT_FOUND)
            if not slackapi.logger_warning(messages.TEAM_NOT_FOUND):
                logger.warn(messages.SLACK_POST_LOG_FAILED)
            try:
                database.save_request_log(request, False, db_messages.TEAM_NOT_FOUND)
            except exceptions.SaveRequestLogError:
                logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
            responder.list_team_transactions_delayed_reply_team_not_existant(request)
            return
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TEAM_SEARCH_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TEAM_SEARCH_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TEAM_SEARCH_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return

    try:
        # Retrieving from the database
        transactions = database.get_last_team_transactions(team_id, transactions_quantity)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TRANSACTIONS_LIST_SEARCH_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.LIST_TRANSACTIONS_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_team_transactions_delayed_reply_success(request, transactions)

def list_all_transactions_dispatcher(request):
    """Dispatcher to list all transactions requests/commands."""
    logger.info(messages.REQUEST_LIST_ALL_TRANSACTIONS_START)
    if not slackapi.logger_info(messages.REQUEST_LIST_ALL_TRANSACTIONS_START):
        logger.warn(messages.SLACK_POST_LOG_FAILED)

    # Check if user is in the users table
    if not user_exists_or_save_new_user(request):
        return

    # Security check
    if not security.user_has_permission(security.RoleLevels.Admin, request["user_id"]):
        logger.warn(messages.INSUFFICIENT_PERMISSIONS)
        if not slackapi.logger_warning(messages.INSUFFICIENT_PERMISSIONS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.UNAUTHORIZED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.unauthorized_error(request)
        return

    # Check if arguments are good
    request_args = get_request_args(request["text"])
    if not request_args or len(request_args) < 1:
        # Bad usage
        logger.warn(messages.MISSING_ARGS)
        if not slackapi.logger_warning(messages.MISSING_ARGS):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.MISSING_ARGS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_all_transactions_delayed_reply_missing_args(request)
        return

    try:
        transactions_quantity = parse_transaction_quantity(request_args[0])
    except exceptions.IntegerParseError as ex:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

    if transactions_quantity <= 0:
        transactions_quantity = definitions.DEFAULT_TRANSACTION_LIST_LENGTH

   # Check if value is not above the max
    if transactions_quantity > definitions.DATABASE_MAX_LIMIT:
        transactions_quantity = definitions.DATABASE_MAX_LIMIT

    try:
        # Retrieve from the database
        transactions = database.get_last_all_transactions(transactions_quantity)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex))
        if not slackapi.logger_critical(messages.TRANSACTIONS_LIST_SEARCH_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.TRANSACTIONS_LIST_SEARCH_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return
    else:
        try:
            database.save_request_log(request, True, db_messages.LIST_TRANSACTIONS_SUCCESS)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.list_all_transactions_delayed_reply_success(request, transactions)

def add_request_to_queue(request):
    """ Add a request to the requests queue."""
    try:
        requests_queue.put(request, block=False)
    except Exception:
        return False
    else:
        return True

def generate_team_entry_code():
    """ Generates and returns a team entry code."""
    # Exceptions will be caught by caller function
    entry_codes = database.get_all_entry_codes()
    new_entry_code = generate_random_code()
    while new_entry_code in entry_codes:
        new_entry_code = generate_random_code()
    return new_entry_code

def generate_random_code(n = 4, rep = 3, sep = '-'):
    return sep.join(["".join(random.choices(string.ascii_uppercase + string.digits, k=n)) for _ in range(rep)])

def generate_uuid4():
    return str(uuid.uuid4())

def get_request_args(args_str):
    return args_str.split()

def get_slack_user_id_from_arg(arg):
    """Gets a slack user id from a string, by regex, with escaped usernames format."""
    regex = r"(?<=@)(.*?)(?=\|)"
    matches = re.search(regex, arg)
    if matches:
        return matches.group(1)
    else:
        return None

def parse_transaction_amount(amount_str):
    try:
        return float(amount_str)
    except Exception as ex:
        raise exceptions.FloatParseError("Failed to convert string to float: {}.".format(ex))

def parse_transaction_quantity(amount_str):
    try:
        return int(amount_str)
    except Exception as ex:
        raise exceptions.IntegerParseError("Failed to convert string to int: {}".format(ex))

def parse_transaction_description(description_list):
    return " ".join(description_list)

def check_valid_uuid4(arg):
    try:
        uuid.UUID(arg, version=4)
    except ValueError:
        return False
    else:
        return True

def user_exists_or_save_new_user(request):
    """ Check if user is already on database or save if not found. Returns False on failure"""
    try:
        if database.user_exists(request['user_id']):
            return True
        else:
            try:
                database.save_user(request["user_id"], request["user_name"])
                return True
            except exceptions.QueryDatabaseError as ex:
                logger.critical(messages.USER_INSERTION_FAILED.format(ex))
                if not slackapi.logger_critical(messages.USER_INSERTION_FAILED.format(ex)):
                    logger.warn(messages.SLACK_POST_LOG_FAILED)
                try:
                    database.save_request_log(request, False, db_messages.USER_ADDITION_FAILED)
                except exceptions.SaveRequestLogError:
                    logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
                responder.delayed_reply_default_error(request)
                return False
    except exceptions.QueryDatabaseError as ex:
        logger.critical(messages.USER_EXISTANCE_CHECK_FAILED.format(ex))
        if not slackapi.logger_critical(messages.USER_EXISTANCE_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        try:
            database.save_request_log(request, False, db_messages.USER_EXISTANCE_CHECK_FAILED)
        except exceptions.SaveRequestLogError:
            logger.warn(messages.REQUEST_LOG_SAVE_FAILED)
        responder.delayed_reply_default_error(request)
        return False