#!/usr/bin/python3

import json
import logging
import socket

from http.server import BaseHTTPRequestHandler, HTTPServer
from http import HTTPStatus

# As defined on `docker-compose.yml`
HOST_PORT = 8000

class ServerRequestHandler(BaseHTTPRequestHandler):

    def handle_not_allowed_method(self, method):
        logging.info("Received not allowed method - {}".format(method))
        self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_header('Content-type','application/json')
        self.end_headers()
        response = {
            "success": False,
            "message": "Method '{}' not allowed".format(method)
        }
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def do_GET(self):
        logging.debug("Got GET request.")
        self.handle_not_allowed_method("GET")

    def do_HEAD(self):
        logging.debug("Got HEAD request.")
        self.handle_not_allowed_method("HEAD")

    def do_PUT(self):
        logging.debug("Got PUT request.")
        self.handle_not_allowed_method("PUT")

    def do_DELETE(self):
        logging.debug("Got DELETE request.")
        self.handle_not_allowed_method("DELETE")

    def do_CONNECT(self):
        logging.debug("Got CONNECT request.")
        self.handle_not_allowed_method("CONNECT")

    def do_OPTIONS(self):
        logging.debug("Got OPTIONS request.")
        self.handle_not_allowed_method("OPTIONS")

    def do_TRACE(self):
        logging.debug("Got TRACE request.")
        self.handle_not_allowed_method("TRACE")

    def do_PATCH(self):
        logging.debug("Got PATCH request.")
        self.handle_not_allowed_method("PATCH")

    def do_POST(self):
        logging.debug("Got POST request.")
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type','text/html')
        self.end_headers()
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info(post_data)
        self.wfile.write(bytes("Data received successfully!", "utf-8"))


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