import psycopg2
import os
import logging as logger
import exceptions
import common
from definitions import INITIAL_TEAM_BALANCE
import log_messages as messages


common.setup_logger()

def connect(autocommit = True):
    """Connects to a PostgreSQL database and returns a connection."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port="5432"
        )
        conn.autocommit = autocommit
        return conn
    except Exception as e:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(e))
        raise exceptions.DatabaseConnectionError("Can't establish connection to database.")

def save_request_log(request, success, description):
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.SaveRequestLogError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO requests (
                token,
                team_id,
                team_domain,
                channel_id,
                channel_name,
                slack_user_id,
                slack_user_name,
                command,
                command_text,
                response_url,
                success,
                description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        data = (
            request['token'],
            request['team_id'],
            request['team_domain'],
            request['channel_id'],
            request['channel_name'],
            request['user_id'],
            request['user_name'],
            request['command'],
            request['text'],
            request['response_url'],
            success,
            description
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.SaveRequestLogError("Could not execute query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def team_name_available(team_name):
    """Checks if a team name is available."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT NOT EXISTS (
                SELECT *
                FROM team_registration
                WHERE team_name = %s
            )
            """
        data = (
            team_name,
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Couldn't not perform database query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def save_team_registration(team_name, entry_code):
    """Saves a team registration entry - Name, ID and Entry code."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO team_registration (
                team_name,
                entry_code
            ) VALUES (%s, %s)
            RETURNING team_id
            """
        data = (
            team_name,
            entry_code
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database insertion query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def user_exists(slack_id):
    """Checks if a user exists in the database."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT EXISTS (
                SELECT *
                FROM users
                WHERE slack_id = %s
            )
            """
        data = (
            slack_id,
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def save_user(slack_id, slack_name):
    """Saves a user exists in the database."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO users (
                slack_id,
                slack_name
            ) VALUES (%s, %s)
            """
        data = (
            slack_id,
            slack_name,
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database insertion query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def user_has_team(slack_id):
    """Checks if a user is already on a team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT EXISTS (
                SELECT team
                FROM users
                WHERE slack_id=%s
                AND team IS NOT NULL
            )
            """
        data = (
            slack_id,
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def valid_entry_code(entry_code):
    """Checks if an entry code is valid."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT team_id, team_name
            FROM team_registration
            WHERE entry_code=%s
            """
        data = (
            entry_code,
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database query: {}".format(ex))
        else:
            db_results = cursor.fetchone()
            if cursor.rowcount != 1:
                cursor.close()
                db_connection.close()
                return dict()
            else:
                result = {
                    "id": db_results[0],
                    "name": db_results[1]
                }
                cursor.close()
                db_connection.close()
                return result

def is_team_created(team_id):
    """Checks if a team is created."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT EXISTS (
                SELECT *
                FROM teams
                WHERE team_id=%s
            )
            """
        data = (
            team_id,
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def create_team(team_info):
    """Creates a new team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO teams (
                team_id,
                team_name,
                balance,
                slack_channel_id
            ) VALUES (%s, %s, %s, %s)
            """
        data = (
            team_info["id"],
            team_info["name"],
            INITIAL_TEAM_BALANCE,
            team_info["channel_id"]
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database insertion query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def add_user_to_team(user_slack_id, team_id):
    """Adds a user to a team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            UPDATE users
            SET team=%s
            WHERE slack_id=%s
            """
        data = (
            team_id,
            user_slack_id
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database update query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def get_users_balance(user_slack_id):
    """Get a user's balance."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT team_name, balance
            FROM teams
            WHERE team_id IN (
                SELECT team
                FROM users
                WHERE slack_id=%s
            )
            """
        data = (
            user_slack_id,
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database update query: {}".format(ex))
        else:
            result = cursor.fetchone()
            cursor.close()
            db_connection.close()
            return result

def users_with_different_team(slack_user_id_1, slack_user_id_2):
    """Checks if two users are in different teams."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT COUNT(DISTINCT team)
            FROM public.users
            WHERE slack_id IN (%s, %s)
            """
        data = (
            slack_user_id_1, slack_user_id_2,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database update query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result == 2

def user_has_enough_credit(slack_user_id, amount):
    """Checks if a user has enough credit."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT EXISTS (
                SELECT
                FROM teams
                WHERE team_id IN (
                    SELECT team
                    FROM public.users
                    WHERE slack_id=%s
                )
                AND balance > %s
            )
            """
        data = (
            slack_user_id, amount,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database update query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def perform_buy(origin_slack_user_id, destination_slack_user_id, amount, description):
    """Performs a shop operation between the two users."""
    try:
        db_connection = connect(False)
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string_1 = """
            UPDATE teams
            SET balance = balance - %s
            WHERE team_id IN (
                SELECT team
                FROM users
                WHERE slack_id = %s
            )
            """
        data_1 = (
            amount, origin_slack_user_id
        )

        sql_string_2 = """
            UPDATE teams
            SET balance = balance + %s
            WHERE team_id IN (
                SELECT team
                FROM users
                WHERE slack_id = %s
            )
            """
        data_2 = (
            amount, destination_slack_user_id
        )

        sql_string_3 = """
            INSERT INTO transactions (
                origin_user_id,
                destination_user_id,
                amount, description
            )
            SELECT origin.user_id, destination.user_id, %s, %s
            FROM (
                SELECT user_id
                FROM users
                WHERE slack_id=%s
            ) origin
            CROSS JOIN (
                SELECT user_id
                FROM users
                WHERE slack_id=%s
            ) destination
            """
        data_3 = (
            amount, description, origin_slack_user_id, destination_slack_user_id
        )

        try:
            cursor.execute(sql_string_1, data_1)
            cursor.execute(sql_string_2, data_2)
            cursor.execute(sql_string_3, data_3)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.rollback()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database operations: {}".format(ex))
        else:
            cursor.close()
            db_connection.commit()
            db_connection.close()

def get_slack_name(slack_user_id):
    """ Gets the slack name of a user."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT slack_name
            FROM users
            WHERE slack_id = %s
        """
        data = (
            slack_user_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def get_last_transactions(slack_user_id, max_quantity):
    """ Gets the last transactions of a team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        # NOTE: Multiple operations, change to having more info on the table?
        sql_string = """
            SELECT
                transactions.created_at,
                u1.slack_id AS origin_slack_id,
                u1.slack_name AS origin_slack_name,
                u2.slack_id AS destination_slack_id,
                u2.slack_name AS destination_slack_name,
                transactions.amount,
                transactions.description
            FROM transactions
            INNER JOIN users u1
            ON transactions.origin_user_id = u1.user_id
            INNER JOIN users u2
            ON transactions.destination_user_id = u2.user_id
            WHERE transactions.origin_user_id IN (
                SELECT users.user_id
                FROM users
                WHERE users.team IN (
                    SELECT team
                    FROM users
                    WHERE slack_id=%s
                )
            )
            OR transactions.destination_user_id IN (
                SELECT user_id
                FROM users
                WHERE team IN (
                    SELECT team
                    FROM users
                    WHERE slack_id=%s
                )
            )
            ORDER BY created_at DESC
            LIMIT %s
        """
        data = (
            slack_user_id, slack_user_id, max_quantity
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def get_teams():
    """ Gets the teams list."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT team_id, team_name
            FROM teams
        """
        try:
            cursor.execute(sql_string)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def get_teams_registration():
    """ Gets the registration teams list."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT team_id, team_name, entry_code
            FROM team_registration
        """
        try:
            cursor.execute(sql_string)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def get_team_details(team_id):
    """ Gets a team details."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT team_id, team_name, balance
            FROM teams
            WHERE team_id = %s
        """
        data = (
            team_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = cursor.fetchone()
            cursor.close()
            db_connection.close()
            return result

def get_team_users(team_id):
    """ Gets a team users."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT slack_id, slack_name, user_id
            FROM users
            WHERE team = %s
        """
        data = (
            team_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def get_user_details_from_slack_id(slack_id):
    """ Gets an user details from its slack id."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT slack_id, slack_name, user_id, team
            FROM users
            WHERE slack_id = %s
        """
        data = (
            slack_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = cursor.fetchone()
            cursor.close()
            db_connection.close()
            return result

def get_user_details_from_user_id(user_id):
    """ Gets an user details from its user id."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT slack_id, slack_name, user_id, team
            FROM users
            WHERE user_id = %s
        """
        data = (
            user_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = cursor.fetchone()
            cursor.close()
            db_connection.close()
            return result

def get_user_permissions(slack_user_id):
    """ Gets users permissions from its slack user id."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT staff_function
            FROM permissions
            WHERE permissions.user_id IN (
                SELECT users.user_id
                FROM users
                WHERE users.slack_id = %s
            )
        """
        data = (
            slack_user_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            if cursor.rowcount > 0:
                result = cursor.fetchone()[0]
                cursor.close()
                db_connection.close()
                return result
            else:
                return None

def get_last_user_transactions(slack_user_id, max_quantity):
    """ Gets the last transactions of a user."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT
                transactions.created_at,
                u1.slack_id AS origin_slack_id,
                u1.slack_name AS origin_slack_name,
                u2.slack_id AS destination_slack_id,
                u2.slack_name AS destination_slack_name,
                transactions.amount,
                transactions.description
            FROM transactions
            INNER JOIN users u1
            ON transactions.origin_user_id = u1.user_id
            INNER JOIN users u2
            ON transactions.destination_user_id = u2.user_id
            WHERE transactions.origin_user_id IN (
                SELECT user_id
                FROM users
                WHERE slack_id = %s
            )
            OR transactions.destination_user_id IN (
                SELECT user_id
                FROM users
                WHERE slack_id = %s
            )
            ORDER BY created_at DESC
            LIMIT %s
        """
        data = (
            slack_user_id, slack_user_id, max_quantity
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def remove_user_permissions(slack_user_id):
    """ Removes users permissions"""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            DELETE FROM permissions
            WHERE user_id IN (
                SELECT user_id
                FROM users
                WHERE slack_id = %s
            )
        """
        data = (
            slack_user_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def user_is_staff(slack_user_id):
    """ Returns True if a user is staff/admin, False otherwise"""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT EXISTS (
                SELECT
                FROM permissions
                WHERE user_id IN (
                    SELECT user_id
                    FROM users
                    WHERE slack_id = %s
                )
            )
        """
        data = (
            slack_user_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def update_user_role(slack_user_id, new_role):
    """Updates a user (staff member) role"""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            UPDATE permissions
            SET staff_function = %s
            WHERE user_id IN (
                SELECT user_id
                FROM users
                WHERE slack_id = %s
            )
        """
        data = (
            new_role, slack_user_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database update query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def add_user_to_staff(slack_user_id, new_role):
    """Adds a user to the staff team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO permissions (
                user_id,
                staff_function
            )
            SELECT users.user_id, %s
            FROM (
                SELECT user_id
                FROM users
                WHERE slack_id = %s
            ) users
        """
        data = (
            new_role, slack_user_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database insert query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def get_staff_team():
    """Returns all staff members."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT
                permissions.user_id,
                permissions.staff_function,
                users.slack_id,
                users.slack_name
            FROM permissions
            INNER JOIN users
            ON users.user_id = permissions.user_id
        """
        try:
            cursor.execute(sql_string)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def all_teams_balance_above(quantity):
    """Returns True if all teams have at least quantity balance."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT EXISTS (SELECT *
            FROM teams
            WHERE balance < %s
            )
        """
        data = (
            quantity,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return not result

def alter_money_to_all_teams(quantity):
    """Updates the balance of all teams."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            UPDATE teams
            SET balance = balance + %s
        """
        data = (
            quantity,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def save_reward(request, amount, description):
    """Saves a reward given to all teams."""

    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.SaveRequestLogError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO rewards (
                given_by,
                amount,
                destination,
                description
            ) SELECT users.user_id, %s, 'ALL TEAMS', %s
            FROM users
            WHERE slack_id = %s
            """
        data = (
            amount,
            description,
            request['user_id'],
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.SaveRequestLogError("Could not execute query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def team_balance_above(team_id, quantity):
    """Returns True if a team balance is above quantity."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT EXISTS (
                SELECT
               FROM TEAMS
                WHERE team_id = %s
                AND balance >= %s
            )
        """
        data = (
            team_id, quantity
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def alter_money_to_team(team_id, quantity):
    """Updates the balance of one team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            UPDATE teams
            SET balance = balance + %s
            WHERE team_id = %s
        """
        data = (
            quantity, team_id
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def save_reward_team(request, team_id, amount, description):
    """Saves a reward given to a team."""

    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.SaveRequestLogError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO rewards (
                given_by,
                amount,
                destination,
                description
            ) SELECT users.user_id, %s, %s, %s
            FROM users
            WHERE slack_id = %s
            """
        data = (
            amount,
            team_id,
            description,
            request['user_id'],
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.SaveRequestLogError("Could not execute query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def get_last_team_transactions(team_id, max_quantity):
    """ Gets the last transactions of a team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        # NOTE: Multiple operations, change to having more info on the table?
        sql_string = """
            SELECT
                transactions.created_at,
                u1.slack_id AS origin_slack_id,
                u1.slack_name AS origin_slack_name,
                u2.slack_id AS destination_slack_id,
                u2.slack_name AS destination_slack_name,
                transactions.amount,
                transactions.description
            FROM transactions
            INNER JOIN users u1
            ON transactions.origin_user_id = u1.user_id
            INNER JOIN users u2
            ON transactions.destination_user_id = u2.user_id
            WHERE transactions.origin_user_id IN (
                SELECT users.user_id
                FROM users
                WHERE users.team = %s
            )
            OR transactions.destination_user_id IN (
                SELECT users.user_id
                FROM users
                WHERE users.team = %s
            )
            ORDER BY created_at DESC
            LIMIT %s
        """
        data = (
            team_id, team_id, max_quantity
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def get_last_all_transactions(max_quantity):
    """ Gets the last transactions of the entire server."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT
                transactions.created_at,
                u1.slack_id AS origin_slack_id,
                u1.slack_name AS origin_slack_name,
                u2.slack_id AS destination_slack_id,
                u2.slack_name AS destination_slack_name,
                transactions.amount,
                transactions.description
            FROM transactions
            INNER JOIN users u1
            ON transactions.origin_user_id = u1.user_id
            INNER JOIN users u2
            ON transactions.destination_user_id = u2.user_id
            ORDER BY created_at DESC
            LIMIT %s
        """
        data = (
            max_quantity,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def get_all_entry_codes():
    """ Gets all entry codes."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            SELECT entry_code
            FROM team_registration
        """
        try:
            cursor.execute(sql_string)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r[0] for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result

def get_team_slack_group_id(team_id):
    """ Gets the slack group id of a team."""

    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()
        sql_string = """
            SELECT slack_channel_id
            FROM teams
            WHERE team_id = %s
        """
        data = (
            team_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            results = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return results

def get_team_slack_group_id_from_slack_user_id(slack_user_id):
    """ Gets the slack group id of a team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()
        sql_string = """
            SELECT slack_channel_id
            FROM teams
            WHERE team_id IN (
                SELECT team
                FROM users
                WHERE slack_id = %s
            )
        """
        data = (
            slack_user_id,
        )
        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            if cursor.rowcount == 1:
                results = cursor.fetchone()[0]
            else:
                results = None

            cursor.close()
            db_connection.close()
            return results

def get_all_teams_slack_group_id():
    """ Gets the slack group id of all teams."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        logger.critical(messages.CONNECT_TO_DB_FAILED.format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()
        sql_string = """
            SELECT slack_channel_id
            FROM teams
        """
        try:
            cursor.execute(sql_string)
        except Exception as ex:
            logger.critical(messages.DB_EXECUTE_FAILED.format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database select query: {}".format(ex))
        else:
            result = [r[0] for r in cursor.fetchall()]
            cursor.close()
            db_connection.close()
            return result
