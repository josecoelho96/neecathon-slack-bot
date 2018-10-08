from bottle import response
import json
import exceptions
import os
import requests
import logging as logger
import common
import database
import datetime
import responder_messages as messages
import log_messages
import slackapi


common.setup_logger()

def confirm_command_reception():
    """Immediate response to a request."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": messages.REQUEST_RECEIVED
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def create_team_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting not enough arguments on create team command"""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.CREATE_TEAM_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def create_team_delayed_reply_name_exists(request, team_name):
    """Delayed response to Slack reporting impossibility to create team as name already exists"""
    response_content = {
        "text": messages.TEAM_NAME_ALREADY_EXISTS.format(team_name)
    }
    send_delayed_response(request['response_url'], response_content)

def create_team_delayed_reply_success(request, team_id, team_name, team_entry_code):
    """Delayed response to Slack reporting a new team creation"""
    response_content = {
        "text": messages.TEAM_REGISTRATION_SUCCESS,
        "attachments": [
            {
                "text": messages.TEAM_REGISTRATION_DETAILS.format(team_name, team_entry_code, team_id)
            }
        ]
    }
    send_delayed_response(request['response_url'], response_content)

def join_team_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting not enough arguments on join team command"""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.JOIN_TEAM_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def join_team_delayed_reply_already_on_team(request):
    """Delayed response to Slack reporting user is already on a team on join team command"""
    response_content = {
        "text": messages.USER_ALREADY_ON_TEAM_ERROR.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def join_team_delayed_reply_invalid_code(request):
    """Delayed response to Slack reporting an invalid code."""
    response_content = {
        "text": messages.INVALID_CODE
    }
    send_delayed_response(request['response_url'], response_content)

def join_team_delayed_reply_success(request, team_name):
    """Delayed response to Slack reporting user joined team."""
    response_content = {
        "text": messages.JOIN_TEAM_SUCCESS.format(team_name)
    }
    send_delayed_response(request['response_url'], response_content)

def check_balance_delayed_reply_no_team(request):
    """Delayed response to Slack reporting that user has no team."""
    response_content = {
        "text": messages.CHECK_BALANCE_USER_HAS_NO_TEAM.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def check_balance_delayed_reply_success(request, team, balance):
    """Delayed response to Slack reporting the user's balance."""
    response_content = {
        "text": messages.CHECK_BALANCE_SUCCESS,
        "attachments": [
            {
                "text": messages.CHECK_BALANCE_DETAILS.format(team, balance)
            }
        ]
    }
    send_delayed_response(request['response_url'], response_content)

def buy_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting not enough arguments on buy command"""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.BUY_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def buy_delayed_reply_no_team(request):
    """Delayed response to Slack reporting that user has no team."""
    response_content = {
        "text": messages.BUY_USER_HAS_NO_TEAM.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def buy_delayed_reply_no_user_arg(request):
    """Delayed response to Slack reporting that first arg is not a user."""
    response_content = {
        "text": messages.BUY_NO_DESTINATION_USER
    }
    send_delayed_response(request['response_url'], response_content)

def buy_delayed_reply_destination_himself(request):
    """Delayed response to Slack reporting that destination is the owner user."""
    response_content = {
        "text": messages.BUY_DESTINATION_ORIGIN_SAME.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def buy_delayed_reply_destination_no_team(request):
    """Delayed response to Slack reporting that destination user has no team."""
    response_content = {
        "text": messages.BUY_DESTINATION_NO_TEAM.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def buy_delayed_reply_destination_same_team(request):
    """Delayed response to Slack reporting that destination user is in the same team as origin."""
    response_content = {
        "text": messages.BUY_DESTINATION_SAME_TEAM.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def delayed_reply_invalid_value(request):
    """Delayed response to Slack reporting that the amount is invalid."""
    response_content = {
        "text": messages.INVALID_VALUE.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def buy_delayed_reply_not_enough_money(request):
    """Delayed response to Slack reporting that the user doesn't have enough money."""
    response_content = {
        "text": messages.BUY_NOT_ENOUGH_MONEY.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def buy_delayed_reply_success(request, destination_slack_user_id):
    """Delayed response to Slack reporting that a transaction was successfull."""
    response_content = {
        "text": messages.BUY_SUCCESS.format(get_slack_user_tag(destination_slack_user_id))
    }
    send_delayed_response(request['response_url'], response_content)

def list_transactions_delayed_reply_no_team(request):
    """Delayed response to Slack reporting that user has no team."""
    response_content = {
        "text": messages.LIST_TRANSACTIONS_USER_HAS_NO_TEAM.format(get_support_channel_id())
    }
    send_delayed_response(request['response_url'], response_content)

def list_transactions_delayed_reply_success(request, transaction_list):
    """Delayed response to Slack reporting the last quantity transactions made."""
    response_content = {
        "text": messages.LIST_TRANSACTIONS_SUCCESS.format(len(transaction_list)),
    }

    for idx, transaction in enumerate(transaction_list):
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_INDEX.format(idx + 1, len(transaction_list))
        # Check if origin / destination is the user that made the request
        if transaction[1] == request["user_id"]:
            # I'm the origin
            response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_ORIGIN_ME.format(transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        elif transaction[3] == request["user_id"]:
            # I'm the destination
            response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_DESTINATION_ME.format(transaction[1], transaction[2], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        else:
            # I'm none of the ones above
            response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION.format(transaction[1], transaction[2], transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))

        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_AMOUNT.format(transaction[5], transaction[6])

    send_delayed_response(request['response_url'], response_content)

def list_teams_delayed_reply_success(request, teams_list):
    """Delayed response to Slack reporting the teams list."""
    response_content = {
        "text": messages.LIST_TEAMS_SUCCESS.format(len(teams_list)),
    }
    for idx, team in enumerate(teams_list):
        response_content["text"] += messages.LIST_TEAMS_TEAM_DETAILS.format(idx + 1, team[1], team[0])

    send_delayed_response(request['response_url'], response_content)

def list_teams_registration_delayed_reply_success(request, teams_list):
    """Delayed response to Slack reporting the registration teams list."""
    response_content = {
        "text": messages.LIST_REGISTRATION_TEAMS_SUCCESS.format(len(teams_list)),
    }
    for idx, team in enumerate(teams_list):
        response_content["text"] += messages.LIST_REGISTRATION_TEAMS_TEAM_DETAILS.format(idx + 1, team[1], team[0], team[2])

    send_delayed_response(request['response_url'], response_content)

def team_details_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting a bad usage on team details command."""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.TEAM_DETAILS_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def team_details_delayed_reply_success(request, details, users):
    """Delayed response to Slack reporting the results of team details command."""

    response_content = {
        "text": "",
    }
    if len(details):
        response_content["text"] += messages.TEAM_DETAILS_SUCCESS
        response_content["text"] += messages.TEAM_DETAILS_DETAILS.format(details[1], details[2], details[0])
        if len(users):
            # Team has users
            for user in users:
                response_content["text"] += messages.TEAM_DETAILS_ELEMENT_DETAILS.format(user[0], user[1], user[2])
        else:
            # Team has no users
            response_content["text"] += messages.TEAM_DETAILS_SUCCESS_NO_ELEMENTS
    else:
        # No team
        response_content["text"] += messages.TEAM_DETAILS_SUCCESS_NO_TEAM

    send_delayed_response(request['response_url'], response_content)

def user_details_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting a bad usage on user details command."""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.USER_DETAILS_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def user_details_delayed_reply_success(request, user_info):
    """Delayed response to Slack reporting the results of user details command."""
    if user_info:
        response_content = {
            "text": messages.USER_DETAILS_SUCCESS.format(user_info[0], user_info[1], user_info[2], user_info[3]),
        }
    else:
        response_content = {
            "text": messages.USER_DETAILS_SUCCESS_NO_USER
        }
    send_delayed_response(request['response_url'], response_content)

def list_user_transactions_delayed_reply_success(request, transaction_list):
    """Delayed response to Slack reporting the last quantity transactions made by user."""
    response_content = {
        "text": messages.LIST_USER_TRANSACTIONS_SUCCESS.format(len(transaction_list)),
    }

    for idx, transaction in enumerate(transaction_list):
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_INDEX.format(idx + 1, len(transaction_list))
        # Check if origin / destination is the user that made the request
        if transaction[1] == request["user_id"]:
            # I'm the origin
            response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_ORIGIN_ME.format(transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        elif transaction[3] == request["user_id"]:
            # I'm the destination
            response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_DESTINATION_ME.format(transaction[1], transaction[2], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        else:
            # I'm none of the ones above
            response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION.format(transaction[1], transaction[2], transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))

        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_AMOUNT.format(transaction[5], transaction[6])

    send_delayed_response(request['response_url'], response_content)

def change_permission_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting a bad usage on change permission command."""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.CHANGE_PERMISSIONS_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def change_permission_delayed_reply_success(request):
    """Delayed response to Slack reporting success change permission command."""
    response_content = {
        "text": messages.CHANGE_PERMISSIONS_SUCCESS,
    }
    send_delayed_response(request['response_url'], response_content)

def list_staff_delayed_reply_success(request, staff_team):
    """Delayed response to Slack reporting the staff team."""
    response_content = {
        "text": messages.LIST_STAFF_SUCCESS,
    }

    for element in staff_team:
        response_content["text"] += messages.LIST_STAFF_DETAILS.format(element[2], element[3], element[1], element[0])

    send_delayed_response(request['response_url'], response_content)

def hackerboy_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting a bad usage on hackerboy command."""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.HACKERBOY_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def hackerboy_delayed_reply_not_enough_money_on_some_teams(request, amount):
    """Delayed response to Slack reporting some teams will get a negative amount on hackerboy command."""
    response_content = {
        "text": messages.HACKERBOY_NOT_ENOUGH_MONEY.format(amount),
    }
    send_delayed_response(request['response_url'], response_content)

def hackerboy_delayed_reply_success(request, amount):
    """Delayed response to Slack reporting success hackerboy command."""

    if amount > 0:
        response_content = {
            "text": messages.HACKERBOY_SUCCESS_ADD.format(amount),
        }
    elif amount < 0:
        response_content = {
            "text": messages.HACKERBOY_SUCCESS_SUB.format(abs(amount)),
        }
    else:
        response_content = {
            "text": messages.HACKERBOY_SUCCESS_ZERO,
        }
    send_delayed_response(request['response_url'], response_content)

def hackerboy_team_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting a bad usage on team hackerboy command."""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.HACKERBOY_TEAM_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def hackerboy_team_delayed_reply_not_enough_money(request, amount):
    """Delayed response to Slack reporting that a team will get a negative amount on  team hackerboy command."""
    response_content = {
        "text": messages.HACKERBOY_TEAM_NOT_ENOUGH_MONEY.format(amount)
    }
    send_delayed_response(request['response_url'], response_content)

def hackerboy_team_delayed_reply_success(request, amount):
    """Delayed response to Slack reporting success team hackerboy command."""

    if amount > 0:
        response_content = {
            "text": messages.HACKERBOY_TEAM_SUCCESS_ADD.format(amount),
        }
    elif amount < 0:
        response_content = {
            "text": messages.HACKERBOY_TEAM_SUCCESS_SUB.format(amount),
        }
    else:
        response_content = {
            "text": messages.HACKERBOY_TEAM_SUCCESS_ZERO,
        }
    send_delayed_response(request['response_url'], response_content)

def list_user_transactions_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting a bad usage on list user transactions command."""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.LIST_USER_TRANSACTIONS_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def delayed_reply_user_has_no_team(request):
    """Delayed response to Slack reporting that an user has no team."""
    response_content = {
        "text": messages.USER_HAS_NO_TEAM,
    }
    send_delayed_response(request['response_url'], response_content)

def list_to_admin_user_transactions_delayed_reply_success(request, transaction_list):
    """Delayed response to Slack reporting the last quantity transactions made an user."""
    response_content = {
        "text": messages.LIST_ADMIN_USER_TRANSACTIONS_SUCCESS.format(len(transaction_list)),
    }

    for idx, transaction in enumerate(transaction_list):
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_INDEX.format(idx + 1, len(transaction_list))
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION.format(transaction[1], transaction[2], transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_AMOUNT.format(transaction[5], transaction[6])

    send_delayed_response(request['response_url'], response_content)

def list_team_transactions_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting a bad usage on list team transactions command."""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.LIST_TEAM_TRANSACTIONS_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def list_team_transactions_delayed_reply_team_not_existant(request):
    """Delayed response to Slack reporting a non existant team on list team transactions command."""
    response_content = {
        "text": messages.TEAM_NOT_FOUND
    }
    send_delayed_response(request['response_url'], response_content)

def list_team_transactions_delayed_reply_success(request, transaction_list):
    """Delayed response to Slack reporting the last quantity transactions made a team."""
    response_content = {
        "text": messages.LIST_TEAMS_TRANSACTIONS_SUCCESS.format(len(transaction_list)),
    }

    for idx, transaction in enumerate(transaction_list):
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_INDEX.format(idx + 1, len(transaction_list))
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION.format(transaction[1], transaction[2], transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_AMOUNT.format(transaction[5], transaction[6])

    send_delayed_response(request['response_url'], response_content)

def list_all_transactions_delayed_reply_missing_args(request):
    """Delayed response to Slack reporting a bad usage on list all transactions command."""
    response_content = {
        "text": messages.BAD_COMMAND_USAGE + messages.LIST_ALL_TRANSACTIONS_COMMAND_USAGE
    }
    send_delayed_response(request['response_url'], response_content)

def list_all_transactions_delayed_reply_success(request, transaction_list):
    """Delayed response to Slack reporting the last quantity transactions made overall."""
    response_content = {
        "text": messages.LIST_ALL_TRANSACTIONS_SUCCESS.format(len(transaction_list)),
    }
    for idx, transaction in enumerate(transaction_list):
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_INDEX.format(idx + 1, len(transaction_list))
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION.format(transaction[1], transaction[2], transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        response_content["text"] += messages.LIST_TRANSACTIONS_TRANSACTION_AMOUNT.format(transaction[5], transaction[6])

    send_delayed_response(request['response_url'], response_content)

def default_error():
    """Immediate default response to report an error."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": messages.DEFAULT_ERROR.format(get_support_channel_id()),
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def delayed_reply_default_error(request):
    """Delayed default response to report an error."""
    response_content = {
        "text": messages.DEFAULT_ERROR.format(get_support_channel_id()),
    }
    send_delayed_response(request['response_url'], response_content)

def overloaded_error():
    """Immediate default response to an overloaded error."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": messages.OVERLOADED_ERROR.format(get_support_channel_id()),
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def unverified_origin_error():
    """Immediate default response to an unverified origin error."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": messages.UNVERIFIED_ORIGIN_ERROR.format(get_support_channel_id()),
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def unauthorized_error(request):
    """Delayed response to Slack reporting no authorization."""
    response_content = {
        "text": messages.UNAUTHORIZED.format(get_support_channel_id()),
    }
    send_delayed_response(request['response_url'], response_content)

def get_support_channel_id():
    """Get slack support channel id."""
    return os.getenv("SLACK_SUPPORT_CHANNEL_ID")

def send_delayed_response(url, content):
    """Send a POST request to Slacsend_delayed_responsesend_delayed_responsek with JSON body."""
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, json=content, headers=headers)
        if not r.status_code == 200:
            logger.critical(log_messages.DELAYED_MESSAGE_POST_FAILED_BAD_HTTP_CODE.format(r.status_code))
            if not slackapi.logger_critical(log_messages.DELAYED_MESSAGE_POST_FAILED_BAD_HTTP_CODE.format(r.status_code)):
                logger.warn(log_messages.SLACK_POST_LOG_FAILED)
    except requests.exceptions.RequestException as ex:
        logger.critical(log_messages.DELAYED_MESSAGE_POST_FAILED.format(ex))
        if not slackapi.logger_critical(log_messages.DELAYED_MESSAGE_POST_FAILED.format(ex)):
            logger.warn(log_messages.SLACK_POST_LOG_FAILED)

def get_slack_user_tag(slack_user_id):
    """Gets user information from database to build Slack like @user"""
    try:
        slack_user_name = database.get_slack_name(slack_user_id)
        return "<@{}|{}>".format(slack_user_id, slack_user_name)
    except exceptions.QueryDatabaseError as ex:
        logger.critical(log_messages.DB_EXECUTE_FAILED.format(ex))
        if not slackapi.logger_critical(log_messages.DB_EXECUTE_FAILED.format(ex)):
            logger.warn(log_messages.SLACK_POST_LOG_FAILED)
        return None
