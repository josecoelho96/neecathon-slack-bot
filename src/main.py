#!/usr/bin/env python3

import common
import exceptions
import logging as log
import server
import dispatcher

def main():
    common.setup_logger()
    try:
        # Start dispatcher
        dispatcher.start()
        # Start http server
        server.start()
    except exceptions.HTTPServerStartError as ex:
        log.error("Server not started. Exiting. Details: {}".format(ex))

if __name__ == "__main__":
    main()
