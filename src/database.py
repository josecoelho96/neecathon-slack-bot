import psycopg2
import os
import logging as log
import exceptions
import common


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
            raise exceptions.QueryDatabaseError("Could not perform database query.")
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
            raise exceptions.QueryDatabaseError("Could not perform database insertion query.")
        else:
            cursor.close()
            db_connection.close()