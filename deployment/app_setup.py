#!/usr/bin/env python3

import logging as logger
import requests

def set_headers(user_token):
    """ Sets the appropriate headers."""
    token = user_token
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Bearer " + token
    }
    return headers

def create_channel(channel_name, user_token):
    """ Creates a new public channel."""
    url = "https://slack.com/api/channels.create"
    headers = set_headers(user_token)
    payload = {
        "name": channel_name,
    }
    try:
        r = requests.post(url, json = payload, headers = headers)
    except Exception as ex:
        logger.error("Error POSTing: {}".format(ex))
    else:
        req_response = r.json()
        if r.status_code == 200:
            if req_response["ok"] == True:
                logger.info("Success. Channel created. Details: [ID: {} | Name: {}]".format(req_response["channel"]["id"], req_response["channel"]["name"]))
                return req_response["channel"]["id"]
            else:
                logger.error("Failed. Details: {}".format(req_response["error"]))
        else:
            logger.error("Failed to do the request. Code: {}".format(r.status_code))
        return None


def create_group(group_name, user_token):
    """ Creates a new private channel."""
    url = "https://slack.com/api/groups.create"
    headers = set_headers(user_token)
    payload = {
        "name": group_name,
    }
    try:
        r = requests.post(url, json = payload, headers = headers)
    except Exception as ex:
        logger.error("Error POSTing: {}".format(ex))
    else:
        req_response = r.json()
        if r.status_code == 200:
            if req_response["ok"] == True:
                logger.info("Success. Group created. Details: [ID: {} | Name: {}]".format(req_response["group"]["id"], req_response["group"]["name"]))
                return req_response["group"]["id"]
            else:
                logger.error("Failed. Details: {}".format(req_response["error"]))
        else:
            logger.error("Failed to do the request. Code: {}".format(r.status_code))
        return None

def setup_logger(minium_level = logger.DEBUG):
    """Setups default logging scheme."""
    logger.basicConfig(
        # Format example: [21-10-2018 19:00:45] [INFO] [main > main.py:14] : Message
        format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] : %(message)s',
        level=minium_level
    )

def main():
    """ Main function."""
    setup_logger(minium_level=logger.INFO)

    print("Please provide the information asked in order to setup the application.")
    db_username = input("Database username: ")
    db_password = input("Database password: ")
    db_name = input("Database name: ")
    db_host = input("Database host: ")
    slack_signing_secret = input("Slack signing secret: ")
    slack_user_token = input("Please insert the user token: ")
    slack_logs_channel_id = create_group("logs", slack_user_token)
    slack_staff_channel_id = create_group("staff", slack_user_token)
    slack_support_channel_id = create_channel("suporte", slack_user_token)

    with open(".env", "x") as env_file:
        env_file.write("# Database related\n")
        env_file.write("DB_USERNAME={}\n".format(db_username))
        env_file.write("DB_PASSWORD={}\n".format(db_password))
        env_file.write("DB_NAME={}\n".format(db_name))
        env_file.write("DB_HOST={}\n".format(db_host))

        env_file.write("\n# App related\n")

        env_file.write("\n# Slack related\n")
        env_file.write("SLACK_SUPPORT_CHANNEL_ID={}\n".format(slack_support_channel_id))
        env_file.write("SLACK_SIGNING_SECRET={}\n".format(slack_signing_secret))
        env_file.write("SLACK_USER_TOKEN={}\n".format(slack_user_token))
        env_file.write("SLACK_LOGS_CHANNEL_ID={}\n".format(slack_logs_channel_id))
        env_file.write("SLACK_STAFF_CHANNEL_ID={}\n".format(slack_staff_channel_id))

if __name__ == "__main__":
    main()
