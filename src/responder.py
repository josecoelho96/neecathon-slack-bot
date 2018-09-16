from bottle import response
import json
import exceptions
import os
import requests
import logging as log
import common


common.setup_logger()

def confirm_payout_reception():
    """Immediate response to a request."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Um dos meus macaquinhos vai tratar do teu pedido!",
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def confirm_create_team_command_reception():
    """Immediate response to a create team command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Um dos meus macaquinhos vai tratar de criar a equipa!",
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def confirm_join_team_command_reception():
    """Immediate response to a join team command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Um dos meus macaquinhos vai verificar se podes juntar-te à equipa!",
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def confirm_check_balance_command_reception():
    """Immediate response to a check balance command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Pedi ao Tio Patinhas para procurar os teus detalhes financeiros!",
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def create_team_delayed_reply_missing_arguments(request):
    """Delayed response to Slack reporting not enough arguments on create team command"""
    log.debug("Missing arguments on create team request.")
    response_content = {
        "text": "*ERRO!* Estás a ser totó... \n*Utilização*: ```/criar-equipa <nome da equipa>```"
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def create_team_delayed_reply_name_exists(request, team_name):
    """Delayed response to Slack reporting impossibility to create team as name already exists"""
    log.debug("Send message reporting team name already in use.")
    response_content = {
        "text": "*ERRO!* Uma equipa com o nome '{}' já existe.".format(team_name)
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def create_team_delayed_reply_success(request, team_id, team_name, team_entry_code):
    """Delayed response to Slack reporting a new team creation"""
    log.debug("Send message reporting new team created")
    response_content = {
        "text": "Equipa registada! :banana:\nDetalhes:",
        "attachments": [
            {
                "text":"*Nome*: {}\n*Código*: {}\n*ID*: {}\n".format(team_name, team_entry_code, team_id)
            }
        ]
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def join_team_delayed_reply_missing_arguments(request):
    """Delayed response to Slack reporting not enough arguments on join team command"""
    log.debug("Missing arguments on join team request.")
    response_content = {
        "text": "*ERRO! Utilização*: ```/entrar <código da equipa>```"
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def join_team_delayed_reply_already_on_team(request):
    """Delayed response to Slack reporting user is already on a team on join team command"""
    log.debug("User already on team send a join team request.")
    response_content = {
        "text": "*Já te encontras numa equipa!*\nÉ um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\nPede ajuda no <#{}|suporte>.".format(get_support_channel_id())
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def join_team_delayed_reply_invalid_code(request):
    """Delayed response to Slack reporting an invalid code."""
    log.debug("Invalid entry code on join team request.")
    response_content = {
        "text": "*Código inválido!*\nÉ um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\nPede ajuda no <#{}|suporte>.".format(get_support_channel_id())
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def join_team_delayed_reply_success(request, team_name):
    """Delayed response to Slack reporting user joined team."""
    log.debug("User joined team.")
    response_content = {
        "text": "*Parabéns!*\nFoste adicionado à equipa '{}'".format(team_name)
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def check_balance_delayed_reply_no_team(request):
    """Delayed response to Slack reporting that user has no team."""
    response_content = {
        "text": "*Ainda não te encontras numa equipa!*\nEntra numa equipa com o comando: `/entrar`\nÉ um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\nPede ajuda no <#{}|suporte>."
        .format(get_support_channel_id())
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def check_balance_delayed_reply_success(request, team, balance):
    """Delayed response to Slack reporting the user's balance."""
    log.debug("Send balance details to user.")
    response_content = {
        "text": "Aqui estão os detalhes financeiros da tua conta!",
        "attachments": [
            {
                "text":"*Equipa*: {}\n*Saldo*: {:.2f} :money_with_wings:".format(team, balance)
            }
        ]
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def default_error():
    """Immediate default response to report an error."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "O teu pedido não pode ser processado :speak_no_evil:\n Tenta novamente mais tarde ou pede ajuda no <#{}|suporte>."
        .format(get_support_channel_id()),
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def overloaded_error():
    """Immediate default response to an overloaded error."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Não tenho macaquinhos que cheguem! :hear_no_evil::see_no_evil::speak_no_evil:\nO teu pedido não pode ser processado.\nTenta novamente mais tarde ou pede ajuda no <#{}|suporte>."
        .format(get_support_channel_id()),
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def get_support_channel_id():
    """Get slack support channel id."""
    return os.getenv("SLACK_SUPPORT_CHANNEL_ID")

def send_delayed_response(url, content):
    """Send a POST request to Slack with JSON body."""
    log.debug("Sending delayed response.")
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, json=content, headers=headers)
        log.debug("Post request complete. Code: {}".format(r.status_code))
        return r.status_code == 200
    except requests.exceptions.RequestException as ex:
        log.error("Error while POSTing data to Slack: {}".format(ex))
        raise exceptions.POSTRequestError("Could not perform request: {}".format(ex))