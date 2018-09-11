#!/usr/bin/python3

import logging
import socket

from http.server import BaseHTTPRequestHandler, HTTPServer
from http import HTTPStatus

# As defined on `docker-compose.yml`
HOST_PORT = 8000

class ServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("Got GET request.")
        self.send_response(HTTPStatus.OK)
        self.wfile.write(bytes("Response!", "utf-8"))

def start_http_server(host = '', port = 8000):
    server_address = (host, port)
    server = HTTPServer(server_address, ServerRequestHandler)
    logging.info("HTTP server started [port: {}].".format(port))
    return server

def stop_http_server(server):
    server.server_close()
    logging.info("HTTP server stopped.")

def main():
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s',
        level=logging.DEBUG
    )
    server = start_http_server(port=HOST_PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        stop_http_server(server)

if __name__ == "__main__":
    main()