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
    r = requests.post(url, json = payload, headers = headers)
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
    r = requests.post(url, json = payload, headers = headers)
    req_response = r.json()
    log.debug(req_response)

    return r.status_code == 200 and req_response["ok"] == True