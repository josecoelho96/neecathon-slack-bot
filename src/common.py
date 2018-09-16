import logging as log

def setup_logger():
    """Setups default logging scheme."""
    log.basicConfig(
        format='%(asctime)s - %(levelname)s - (%(threadName)-9s) - %(message)s',
        level=log.DEBUG
    )
