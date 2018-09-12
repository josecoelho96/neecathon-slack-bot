#!/usr/bin/python3

import json
import logging
import socket

from http.server import BaseHTTPRequestHandler, HTTPServer
from http import HTTPStatus
from urllib.parse import parse_qs

# As defined on `docker-compose.yml`
HOST_PORT = 8000

class ServerRequestHandler(BaseHTTPRequestHandler):

    def handle_not_allowed_method(self, method):
        logging.info("Received not allowed method - {}".format(method))
        self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_header('Content-type','application/json')
        self.end_headers()
        response = {
            "message": "Method '{}' not allowed".format(method)
        }
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def handle_length_required(self):
        self.send_response(HTTPStatus.LENGTH_REQUIRED)
        self.send_header('Content-type','application/json')
        self.end_headers()
        response = {
            "message": "'Content-Length' required."
        }
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def handle_internal_server_error(self):
        self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
        self.send_header('Content-type','application/json')
        self.end_headers()
        response = {
            "message": "Server error."
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

        # Get content length or return prematurely
        if self.headers['Content-Length'] is None:
            logging.warn("Header 'Content-Length' wasn't received.")
            self.handle_length_required()
            return # Do not continue

        content_length = 0
        try:
            content_length = int(self.headers['Content-Length'])
        except TypeError as te:
            logging.error("TypeError: Error converting 'Content-Length' header to int: {}".format(te))
            self.handle_internal_server_error()
            return
        except Exception as ex:
            logging.error("Exception: Error converting 'Content-Length' header to int: {}".format(ex))
            self.handle_internal_server_error()
            return

        post_data = parse_qs(self.rfile.read(content_length).decode('utf-8'))
        logging.info(post_data)

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type','application/json')
        self.end_headers()

        response = {
            "text": "O meu assistente está à trabalhar no teu pedido...",
        }

        self.wfile.write(bytes(json.dumps(response), "utf-8"))

        # response = {
        #     "text": "Estas são as informações que o Tio Patinhas tem...",
        #     "attachments": [
        #         {
        #             "title":"Saldo",
        #             "text":"20 mokas"
        #         }
        #     ]
        # }
        # response['attachments'].append({"title":"Vrum","text":"Carro"})
        # response['attachments'].append({"title":"channel-name","text":channel_name})


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