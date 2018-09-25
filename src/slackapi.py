import logging as log
import common
import requests
import os


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
    log.debug("Creating new group")
    headers = set_headers()
    if len(group_name) > 22:
        log.warn("Name will be truncated.")
    payload = {
        "name": group_name,
    }
    try:
        r = requests.post(url, json = payload, headers = headers)
    except Exception as ex:
        log.error("Error while POSTing data to Slack: {}".format(ex))
    else:
        req_response = r.json()
        log.debug(req_response)

        if r.status_code == 200:
            if req_response["ok"] == True:
                return [True, [req_response["group"]["id"], req_response["group"]["name"]]]
            else:
                return [False, req_response["error"]]
        else:
            return [False, "Status code: {}".format(r.status_code)]

def invite_to_group(group_id, user_id):
    """ Invites a user to a private channel."""
    url = "https://slack.com/api/groups.invite"
    log.debug("Inviting new person to group")
    headers = set_headers()
    payload = {
        "channel": group_id,
        "user": user_id
    }
    try:
        r = requests.post(url, json = payload, headers = headers)
    except Exception as ex:
        log.error("Error while POSTing data to Slack: {}".format(ex))
    else:
        req_response = r.json()
        log.debug(req_response)

        return r.status_code == 200 and req_response["ok"] == True

def post_transaction_received_message(channel_id, amount, origin_user):
    message = "Boa! Receberam uma transferência de {}, do <@{}>!".format(amount, origin_user)
    return post_message(channel_id, message)


def post_message(channel_id, message):
    """Post a message on a channel."""
    url = "https://slack.com/api/chat.postMessage"
    log.debug("Inviting new person to group")
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
        log.error("Error while POSTing data to Slack: {}".format(ex))
    else:
        req_response = r.json()
        log.debug(req_response)
        return r.status_code == 200 and req_response["ok"] == True

def post_hackerboy_action_general(team_channel_ids, amount_changed, hacker_message):
    ret_val = True
    for channel_id in team_channel_ids:
        ret_val = ret_val and post_hackerboy_action_team(channel_id, amount_changed, hacker_message)
    return ret_val

def post_hackerboy_action_team(team_channel_id, amount_changed, hacker_message):
    """ Posts a message on a team channel reporting a balance change."""
    if amount_changed > 0:
        message = "O _hackerboy_ é bondoso! Receberam uma transferência de {}!\n".format(amount_changed)
    else:
        message = "O _hackerboy_ decidiu revoltar-se! Perderam {} do vosso saldo!\n".format(amount_changed)

    message += "Ele deixou ainda a seguinte mensagem: '{}'.".format(hacker_message)
    return post_message(team_channel_id, message)
