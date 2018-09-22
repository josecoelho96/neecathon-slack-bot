import common
import database
import exceptions
import logging as log

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
        log.error("Could not perform user permissions check: {}".format(ex))
        return False
    else:
        log.debug(user_permission)
        if not user_permission:
            log.error("User doesn't have any permission.")
            return False

        if role_level[user_permission] >= role_level[level]:
            log.debug("User has permission")
            return True
        else:
            log.error("User doesn't have enough permission.")
            return False