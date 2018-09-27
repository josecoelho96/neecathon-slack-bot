import common
import database
import exceptions
import logging as logger
import log_messages as messages
import slackapi


common.setup_logger()

class RoleLevels:
    Admin = "admin"
    Staff = "staff"

role_level = {
    "admin": 50,
    "staff": 40
}

def user_has_permission(level, user):
    """ Checks if a user has permissions to execute some operation."""
    try:
        user_permission = database.get_user_permissions(user)
    except exceptions.QueryDatabaseError as ex:
        logger.error(messages.USER_PERMISSION_CHECK_FAILED.format(ex))
        if not slackapi.logger_error(messages.USER_PERMISSION_CHECK_FAILED.format(ex)):
            logger.warn(messages.SLACK_POST_LOG_FAILED)
        return False
    else:
        if not user_permission:
            return False
        if role_level[user_permission] >= role_level[level]:
            return True
        else:
            return False
