import logging


class CustomLogger:
    def __init__(self):
        self.logger = logging.getLogger("py_create")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self.logger.addHandler(logging.NullHandler())

    def get_logger(self):
        return self.logger

# Global Instance
logger = CustomLogger().get_logger()