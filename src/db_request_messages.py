"""All messages to save request logs are defined here."""

SERVER_OVERLOADED = "Server overloaded."
REQUEST_ORIGIN_CHECK_FAILED = "Request origin verification failed."
INVALID_REQUEST_COMMAND_VALUE = "Invalid request: 'command' field does not match to any known."
USER_ADDITION_FAILED = "Failed to add user to users table."
USER_EXISTANCE_CHECK_FAILED = "Failed to check user existance on database."
UNAUTHORIZED = "Unauthorized."
MISSING_ARGS = "Not enough arguments."
REGISTRATION_TEAM_SAVE_FAILED = "Failed to save team registration."
REGISTRATION_TEAM_SAVE_SUCCESS = "Team registration saved successfully."
TEAM_NAME_EXISTS = "Team name already in use."
TEAM_NAME_CHECK_FAILED = "Could not verify team name."
USER_ALREADY_ON_TEAM = "User already on team."
USER_HAS_TEAM_CHECK_FAILED = "Failed to check if user has a team."
INVALID_ENTRY_CODE = "Invalid entry code provided."
ENTRY_CODE_VALIDATION_FAILED = "Could not perform entry code validation."
TEAM_CREATION_FAILED = "Team creation failed."
TEAM_SEARCH_FAILED = "Failed to search for the team on the database."
ADD_USER_TO_TEAM_FAILED = "Add user to team failed."
JOIN_TEAM_SUCCESS = "User joined team."
USER_WITHOUT_TEAM = "User has no team."
USER_BALANCE_CHECK_FAILED = "User's team balance check failed."
CHECK_BALANCE_SUCCESS = "Balance retrieved successfully."
ARG_NO_DESTINATION_USER = "Invalid destination user."
DESTINATION_ORIGIN_USER_SAME = "Destination user is the requester."
DESTINATION_USER_WITHOUT_TEAM = "Destination user has no team."
DESTINATION_ORIGIN_SAME_TEAM = "Destination and origin users are in the same team."
DESTINATION_ORIGIN_TEAMS_CHECK_FAILED = "Origin and destination users teams check failed."
TRANSACTION_AMOUNT_PARSING_FAILED = "Failed to parse value to float."
BUY_NON_POSITIVE_AMOUNT = "Non positive transaction amount."
NOT_ENOUGH_CREDIT = "User does not have enough credit."
USER_BALANCE_CHECK_FAILED = "Could not verify user balance."
BUY_OPERATION_FAILED = "Could not perform the transaction."
BUY_SUCCESS = "Transaction succeeded."
TRANSACTIONS_LIST_SEARCH_FAILED = "Could not perform transactions history search."
LIST_TRANSACTIONS_SUCCESS = "Transaction list collected."
TEAM_LIST_RETRIEVE_FAILED = "Teams list search failed."
TEAM_LIST_RETRIEVE_SUCCESS = "Teams list collected."
REGISTRATION_TEAM_LIST_RETRIEVE_FAILED = "Registration teams list search failed."
REGISTRATION_TEAM_LIST_RETRIEVE_SUCCESS = "Registration teams list collected."
TEAM_DETAILS_RETRIEVE_FAILED = "Team details retrieve failed."
TEAM_DETAILS_RETRIEVE_SUCCESS = "Team details collected."
USER_SEARCH_FAILED = "Failed to load user from database."
BAD_USERNAME_FORMAT = "Bad username/ID format."
USER_DETAILS_RETRIEVE_SUCCESS = "User details collected."
UPDATE_USER_PERMISSIONS_FAILED = "Failed to add/update/remove user permissions."
UPDATE_USER_PERMISSONS_SUCCESS = "User permissions updated successfully."
STAFF_TEAM_RETRIEVE_FAILED = "Staff team lookup failed."
STAFF_TEAM_RETRIEVE_SUCCESS = "Staff team retrieved."
PARSING_INVALID_VALUE = "Error parsing, invalid value."
UPDATE_TEAMS_BALANCE_FAILED = "Failed to update all teams balance."
UPDATE_TEAMS_BALANCE_SUCCESS = "All teams balance updated."
HACKERBOY_NOT_ENOUGH_MONEY = "Not enough money on some teams."
HACKERBOY_BALANCE_CHECK_FAILED = "Balance check on teams failed."
UPDATE_TEAM_BALANCE_FAILED = "Failed to update team balance."
UPDATE_TEAM_BALANCE_SUCCESS = "Team balance updated."
HACKERBOY_TEAM_NOT_ENOUGH_MONEY = "Not enough money on team."
HACKERBOY_TEAM_BALANCE_CHECK_FAILED = "Balance check on team failed."
TEAM_NOT_FOUND = "Team not found."
