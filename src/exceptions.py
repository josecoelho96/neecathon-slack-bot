class DatabaseConnectionError(Exception):
    """Raise when a connection to a database can't be established."""

class HTTPServerStartError(Exception):
    """Raise when a HTTP server cannot be started."""

class SaveRequestLogError(Exception):
    """Raise when a request log can't be saved."""

class POSTRequestError(Exception):
    """Raise when a POST request can't be done."""

class QueryDatabaseError(Exception):
    """Raise when a database query can't be done."""