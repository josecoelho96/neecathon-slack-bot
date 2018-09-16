import psycopg2
import os
import logging as log
import exceptions
import common
from definitions import INITIAL_TEAM_BALANCE


common.setup_logger()

def connect():
    """Connects to a PostgreSQL database and returns a connection."""
    log.debug("Connecting to database...")
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host="db",
            port="5432"
        )
        conn.autocommit = True
        log.debug("Connected to database.")
        return conn
    except Exception as e:
        log.critical("Failed to connect to database: {}".format(e))
        raise exceptions.DatabaseConnectionError("Can't establish connection to database.")

def save_request_log(request, success, description):
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        log.error("Could not save request log onto database: {}".format(ex))
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
                user_id,
                user_name,
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
            log.error("Could not save request log onto database: {}".format(ex))
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
        log.critical("Could not verify team name: {}".format(ex))
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
            log.error("Failed to query the database: {}".format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Couldn't not perform database query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def save_team_registration(team_id, team_name, entry_code):
    """Saves a team registration entry - Name, ID and Entry code."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        log.critical("Could save team registration: {}".format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO team_registration (
                team_id,
                team_name,
                entry_code
            ) VALUES (%s, %s, %s)
            """
        data = (
            team_id,
            team_name,
            entry_code
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            log.error("Failed to save team registration on the database: {}".format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database insertion query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()

def user_exists(slack_id):
    """Checks if a user exists in the database."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        log.critical("Could not verify user existance: {}".format(ex))
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
            log.error("Failed to query the database: {}".format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def save_user(slack_id, slack_name, user_id):
    """Saves a user exists in the database."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        log.critical("Could not save user: {}".format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO users (
                slack_id,
                slack_name,
                user_id
            ) VALUES (%s, %s, %s)
            """
        data = (
            slack_id,
            slack_name,
            user_id
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            log.error("Failed to query the database: {}".format(ex))
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
        log.critical("Could not check user's team: {}".format(ex))
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
            log.critical("Could not check user's team: {}".format(ex))
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
        log.critical("Could not check entry code: {}".format(ex))
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
            log.critical("Could not check entry code: {}".format(ex))
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
        log.critical("Could not search for team: {}".format(ex))
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
            log.critical("Could not check team existance: {}".format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database query: {}".format(ex))
        else:
            result = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
            return result

def create_team(team_id, team_name):
    """Creates a new team."""
    try:
        db_connection = connect()
    except exceptions.DatabaseConnectionError as ex:
        log.critical("Couldn't create team: {}".format(ex))
        raise exceptions.QueryDatabaseError("Could not connect to database: {}".format(ex))
    else:
        cursor = db_connection.cursor()

        sql_string = """
            INSERT INTO teams (
                team_id,
                team_name,
                balance
            ) VALUES (%s, %s, %s)
            """
        data = (
            team_id,
            team_name,
            INITIAL_TEAM_BALANCE
        )

        try:
            cursor.execute(sql_string, data)
        except Exception as ex:
            log.error("Failed to create team: {}".format(ex))
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
        log.critical("Couldn't add user to team: {}".format(ex))
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
            log.error("Failed to add user to team: {}".format(ex))
            cursor.close()
            db_connection.close()
            raise exceptions.QueryDatabaseError("Could not perform database update query: {}".format(ex))
        else:
            cursor.close()
            db_connection.close()