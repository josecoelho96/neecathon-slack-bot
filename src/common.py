import logging as logger

def setup_logger(minium_level = logger.DEBUG):
    """Setups default logging scheme."""
    logger.basicConfig(
        # Format example: [21-10-2018 19:00:45] [INFO] [main > main.py:14] : Message
        format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] : %(message)s',
        level=minium_level
    )
