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
}

INITIAL_TEAM_BALANCE = 200

SLACK_REQUEST_TIMESTAMP_MAX_GAP_MINUTES = 1.0
