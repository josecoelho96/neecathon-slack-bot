import logging as logger
import common
import requests
import os
from datetime import datetime
import log_messages as messages
import responder_messages


common.setup_logger()

def set_headers():
    """ Sets the appropriate headers."""
    token = os.getenv("SLACK_USER_TOKEN")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Bearer " + token
    }
    return headers

def create_group(group_name):
    """ Creates a new private channel."""
    url = "https://slack.com/api/groups.create"
    headers = set_headers()
    if len(group_name) > 22:
        logger.warn(messages.SLACK_CHANNEL_NAME_TRUNCATED)
    payload = {
        "name": group_name,
    }
    try:
        r = requests.post(url, json = payload, headers = headers)
    except Exception as ex:
        logger.error(messages.SLACK_POST_FAILED.format(ex))
        if not logger_error(messages.SLACK_POST_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        return [False, [None]]
    else:
        req_response = r.json()
        if r.status_code == 200:
            if req_response["ok"] == True:
                return [True, [req_response["group"]["id"], req_response["group"]["name"]]]
            else:
                return [False, [req_response["error"]]]
        else:
            return [False, ["Status code: {}".format(r.status_code)]]

def invite_to_group(group_id, user_id):
    """ Invites a user to a private channel."""
    url = "https://slack.com/api/groups.invite"
    headers = set_headers()
    payload = {
        "channel": group_id,
        "user": user_id
    }
    try:
        r = requests.post(url, json = payload, headers = headers)
    except Exception as ex:
        logger.error(messages.SLACK_POST_FAILED.format(ex))
        if not logger_error(messages.SLACK_POST_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        return False
    else:
        req_response = r.json()
        return r.status_code == 200 and req_response["ok"] == True

def post_transaction_received_message(channel_id, amount, origin_user):
    message = "Boa! Receberam uma transferência de {}, do <@{}>!".format(amount, origin_user)
    return post_message(channel_id, message)


def post_message(channel_id, message):
    """Post a message on a channel."""
    url = "https://slack.com/api/chat.postMessage"
    headers = set_headers()
    payload = {
        "channel": channel_id,
        "as_user": False,
        "icon_emoji": ":monkey_face:",
        "username": "NEECathon admin",
        "text": message
    }
    try:
        r = requests.post(url, json = payload, headers = headers)
    except Exception as ex:
        logger.error(messages.SLACK_POST_FAILED.format(ex))
        if not logger_error(messages.SLACK_POST_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        return False
    else:
        req_response = r.json()
        return r.status_code == 200 and req_response["ok"] == True

def post_hackerboy_action_general(team_channel_ids, amount_changed, hacker_message):
    ret_val = True
    for channel_id in team_channel_ids:
        ret_val = ret_val and post_hackerboy_action_team(channel_id, amount_changed, hacker_message)
    return ret_val

def post_hackerboy_action_team(team_channel_id, amount_changed, hacker_message):
    """ Posts a message on a team channel reporting a balance change."""
    if amount_changed > 0:
        message = responder_messages.HACKERBOY_TEAM_ADD_MONEY.format(amount_changed)
        message = "O _hackerboy_ é bondoso! Receberam uma transferência de {}!\n".format(amount_changed)
    else:
        message = responder_messages.HACKERBOY_TEAM_REMOVE_MONEY.format(amount_changed)
        message = "O _hackerboy_ decidiu revoltar-se! Perderam {} do vosso saldo!\n".format(amount_changed)

    message += responder_messages.HACKERBOY_TEAM_MESSAGE.format(hacker_message)
    message += "Ele deixou ainda a seguinte mensagem: ' _{}_ '.".format(hacker_message)
    return post_message(team_channel_id, message)

def logger_info(message):
    """ Logs a INFO level message into a Slack channel."""
    return post_log("INFO", message)

def logger_warning(message):
    """ Logs a WARNING level message into a Slack channel."""
    return post_log("WARNING", message)

def logger_error(message):
    """ Logs a ERROR level message into a Slack channel."""
    return post_log("ERROR", message)

def logger_critical(message):
    """ Logs a CRITICAL level message into a Slack channel."""
    return post_log("CRITICAL", message)

def post_log(level, message):
    """Posts a message on a log channel."""
    url = "https://slack.com/api/chat.postMessage"
    logger.debug(messages.SLACK_POSTING_LOG)
    headers = set_headers()

    # Format example: [21-10-2018 19:00:45] [INFO] : Message
    slack_message = "[_{}_] [*{}*] : {}".format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), level, message)

    payload = {
        "channel": os.getenv("SLACK_LOGS_CHANNEL_ID"),
        "as_user": False,
        "icon_emoji": ":male-technologist:",
        "username": "server logger",
        "text": slack_message
    }
    try:
        r = requests.post(url, json = payload, headers = headers)
    except Exception as ex:
        logger.warn(messages.SLACK_POST_LOG_ERROR.format(ex))
    else:
        req_response = r.json()
        if r.status_code == 200 and req_response["ok"] == True:
            return True
        else:
            logger.warn(messages.SLACK_POST_LOG_REQUEST_RESPONSE.format(req_response))
