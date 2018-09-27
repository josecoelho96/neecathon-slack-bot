# HTTP port where the server is being served on
SERVER_PORT = 8888

# Requests must contain all this keys to be valid
SLACK_REQUEST_DATA_KEYS = [
    "token",
    "team_id",
    "team_domain",
    "channel_id",
    "channel_name",
    "user_id",
    "user_name",
    "text",
    "response_url",
]

SLACK_COMMANDS = {
    "CREATE_TEAM": "/criar-equipa",
    "JOIN_TEAM": "/entrar",
    "CHECK_BALANCE": "/saldo",
    "BUY": "/compra",
    "LIST_TRANSACTIONS": "/movimentos",
    "LIST_TEAMS": "/ver-equipas",
    "LIST_TEAMS_REGISTRATION": "/ver-equipas-registo",
    "TEAM_DETAILS": "/detalhes-equipa",
    "USER_DETAILS": "/detalhes",
    "LIST_MY_TRANSACTIONS": "/meus-movimentos",
    "CHANGE_PERMISSIONS": "/alterar-permissoes",
    "LIST_STAFF": "/ver-staff",
    "HACKERBOY": "/hackerboy",
    "HACKERBOY_TEAM": "/hackerboy-equipa",
    "LIST_USER_TRANSACTIONS": "/transacoes-participante",
    "LIST_TEAM_TRANSACTIONS": "/transacoes-equipa",
    "LIST_ALL_TRANSACTIONS": "/transacoes-todas",

}

INITIAL_TEAM_BALANCE = 200

SLACK_REQUEST_TIMESTAMP_MAX_GAP_SECONDS = 60.0

TEAM_CHANNEL_PREFIX = "t_"