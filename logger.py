import logging


class EmailParser:
    @staticmethod
    def get_logger():
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        return logger

# Usage example:
# logger = EmailParser.get_logger()
# logger.info("This is a log message.")
