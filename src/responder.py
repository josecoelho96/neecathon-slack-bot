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

def confirm_list_teams_command_reception():
    """Immediate response to a list teams command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Vou tratar de ir buscar as equipas a participar!",
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def confirm_list_teams_registration_command_reception():
    """Immediate response to a list teams registration command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Vou tratar de ir buscar as equipas registadas!",
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def confirm_team_details_command_reception():
    """Immediate response to a team details command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Vou tratar de ir buscar os detalhes dessa equipa!",
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def confirm_user_details_command_reception():
    """Immediate response to a user details command."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "Vou tratar de ir buscar os detalhes desse utilizador!",
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

def list_teams_delayed_reply_success(request, teams_list):
    """Delayed response to Slack reporting the teams list."""
    response_content = {
        "text": "Aqui estão as {} equipas a participar:\n".format(len(teams_list)),
    }

    for idx, team in enumerate(teams_list):
        log.debug(team)
        response_content["text"] += "_{}_: *Nome:* {} | *ID:* {}\n".format(idx + 1, team[1], team[0])

    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def list_teams_registration_delayed_reply_success(request, teams_list):
    """Delayed response to Slack reporting the registration teams list."""
    response_content = {
        "text": "Aqui estão as {} equipas registadas:\n".format(len(teams_list)),
    }

    for idx, team in enumerate(teams_list):
        log.debug(team)
        response_content["text"] += "_{}_: *Nome:* {} | *ID:* {} | *Código:* {}\n".format(idx + 1, team[1], team[0], team[2])

    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def team_details_delayed_reply_bad_usage(request):
    """Delayed response to Slack reporting a bad usage on team details command."""
    response_content = {
        "text": "Má utilização do comando! Utilização: `/detalhes-equipa id-equipa`.",
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def team_details_delayed_reply_success(request, details, users):
    """Delayed response to Slack reporting the results of team details command."""

    response_content = {
        "text": "",
    }

    if len(details):
        log.debug("Team exists.")
        response_content["text"] += "Aqui estão os detalhes da equipa:\n"
        response_content["text"] += "*Nome:* {} | *Saldo:* {:.2f} | *ID:* {}\n".format(details[1], details[2], details[0])
        if len(users):
            log.debug("Team has users.")
            for user in users:
                response_content["text"] += "_Elemento:_ *Nome:* <@{}|{}> | *ID:* {}\n".format(user[0], user[1], user[2])
        else:
            log.debug("Team has no users")
            response_content["text"] += "Não foi encontrado nenhum jogador na equipa."
    else:
        log.debug("Team doesn't exist.")
        response_content["text"] += "Não foi encontrada nenhuma equipa com esse ID."
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def user_details_delayed_reply_bad_usage(request):
    """Delayed response to Slack reporting a bad usage on user details command."""
    response_content = {
        "text": "Má utilização do comando! Utilização: `/detalhes [@user|user-id]`.\n Podes fornecer tanto o user pelo seu ID, bem como pela @mention.",
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")

def user_details_delayed_reply_success(request, user_info):
    """Delayed response to Slack reporting the results of user details command."""

    if user_info:
        response_content = {
            "text": "*Informação:*\n*Nome:* <@{}|{}> | *ID:* {} | *Equipa:* {}".format(user_info[0], user_info[1], user_info[2], user_info[3]),
        }
    else:
        response_content = {
            "text": "*Informação:* Não foi encontrado nenhum utilizador com esse ID/nome.",
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

def unverified_origin_error():
    """Immediate default response to an overloaded error."""
    response.add_header("Content-Type", "application/json")
    response_content = {
        "text": "O teu pedido tem origens suspeitas...\nO teu pedido não pode ser processado.\nTenta novamente mais tarde ou pede ajuda no <#{}|suporte>."
        .format(get_support_channel_id()),
    }
    return json.dumps(response_content, ensure_ascii=False).encode("utf-8")

def unauthorized_error(request):
    """Delayed response to Slack reporting no authorization."""
    response_content = {
        "text": "*NÃO PODES FAZER ISSO!*\nErro? Pede ajuda no <#{}|suporte>."
        .format(get_support_channel_id()),
    }
    try:
        if send_delayed_response(request['response_url'], response_content):
            log.debug("Delayed message sent successfully.")
        else:
            log.critical("Delayed message not sent.")
    except exceptions.POSTRequestError:
        log.critical("Failed to send delayed message to Slack.")


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
