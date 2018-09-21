from bottle import response
import json
import exceptions
import os
import requests
import logging as log
import common
import database
import datetime

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

def confirm_buy_command_reception():
    """Immediate response to a buy command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Vou tratar do teu pedido de compra!",
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def confirm_list_transactions_command_reception():
    """Immediate response to a list transactions command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Vou tratar de ir buscar os movimentos da tua equipa!",
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

def buy_delayed_reply_missing_arguments(request):
    """Delayed response to Slack reporting not enough arguments on buy command"""
    log.debug("Missing arguments on buy request.")
    response_content = {
        "text": "*ERRO!* Estás a ser totó... \n*Utilização*: ```/compra <utilizador de destino> <quantia> <descrição>```"
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def delayed_reply_no_team(request):
    """Delayed response to Slack reporting that user has no team."""
    response_content = {
        "text": "*Ainda não te encontras numa equipa!* Só podes fazer compras se fizeres parte de uma equipa.\nEntra numa equipa com o comando: `/entrar`\nÉ um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\nPede ajuda no <#{}|suporte>."
        .format(get_support_channel_id())
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def buy_delayed_reply_no_user_arg(request):
    """Delayed response to Slack reporting that first arg is not a user."""
    response_content = {
        "text": "*Erro!* Deves indicar o utilizador de destino.\nUtilização: `/compra @user quantia descrição`"
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def buy_delayed_reply_destination_himself(request):
    """Delayed response to Slack reporting that destination is the owner user."""
    response_content = {
        "text": "*Erro!* Não podes dar dinheiro a ti próprio :thinking_face:"
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def buy_delayed_reply_destination_no_team(request):
    """Delayed response to Slack reporting that destination user has no team."""
    response_content = {
        "text": "*O destinatário ainda não tem equipa!*\nÉ um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\nPede ajuda no <#{}|suporte>."
        .format(get_support_channel_id())
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def buy_delayed_reply_destination_same_team(request):
    """Delayed response to Slack reporting that destination user is in the same team as origin."""
    response_content = {
        "text": "*O destinatário está na tua equipa!*\nÉ um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\nPede ajuda no <#{}|suporte>."
        .format(get_support_channel_id())
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def delayed_reply_invalid_value(request):
    """Delayed response to Slack reporting that the amount is invalid."""
    response_content = {
        "text": "*Erro!* O valor introduzido é inválido!\nÉ um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\nPede ajuda no <#{}|suporte>."
        .format(get_support_channel_id())
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def buy_delayed_reply_not_enough_money(request):
    """Delayed response to Slack reporting that the user doesn't have enough money."""
    response_content = {
        "text": "*Erro!* Não tens dinheiro suficiente!\nÉ um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\nPede ajuda no <#{}|suporte>."
        .format(get_support_channel_id())
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def buy_delayed_reply_success(request, destination_slack_user_id):
    """Delayed response to Slack reporting that a transaction was successfull."""
    response_content = {
        "text": "*Sucesso!* A tua transferência para o {} foi realizada com sucesso!"
        .format(get_slack_user_tag(destination_slack_user_id))
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def list_transactions_delayed_reply_success(request, transaction_list):
    """Delayed response to Slack reporting the last quantity transactions made."""
    response_content = {
        "text": "Aqui tens os detalhes dos últimos {} movimentos da tua equipa:\n".format(len(transaction_list)),
    }

    for idx, transaction in enumerate(transaction_list):
        log.debug(transaction)
        response_content["text"] += "_Movimento {} de {}:_\n".format(idx + 1, len(transaction_list))
        # Check if origin / destination is the user that made the request
        if transaction[1] == request["user_id"]:
            # I'm the origin
            response_content["text"] += "*De:* mim | *Para:* <@{}|{}> | *Data:* {}\n".format(transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        elif transaction[3] == request["user_id"]:
            # I'm the destination
            response_content["text"] += "*De:* <@{}|{}> | *Para:* mim | *Data:* {}\n".format(transaction[1], transaction[2], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))
        else:
            # I'm none of the ones above
            response_content["text"] += "*De:* <@{}|{}> | *Para:* <@{}|{}> | *Data:* {}\n".format(transaction[1], transaction[2], transaction[3], transaction[4], datetime.datetime.strftime(transaction[0], "%Y-%m-%d %H:%M:%S"))

        response_content["text"] += "*Valor:* {:.2f} | *Descrição:* {}\n\n".format(transaction[5], transaction[6])

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

def unverified_origin_error():
    """Immediate default response to an overloaded error."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "O teu pedido tem origens suspeitas...\nO teu pedido não pode ser processado.\nTenta novamente mais tarde ou pede ajuda no <#{}|suporte>."
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

def get_slack_user_tag(slack_user_id):
    """Gets user information from database to build Slack like @user"""
    try:
        slack_user_name = database.get_slack_name(slack_user_id)
        return "<@{}|{}>".format(slack_user_id, slack_user_name)
    except exceptions.QueryDatabaseError as ex:
        log.warn("Failed to get destination Slack tag: {}".format(ex))
        return None
