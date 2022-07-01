import logging
from logging import handlers


class MyLog:
    def __init__(self, name, file, access):
        self.logger = logging.getLogger(name)
        self.handler = handlers.RotatingFileHandler(f"logs/{file}", access, 0x5000, 1)
        self.Configure_Logger()
        self.log = self.logger.info

    def Configure_Logger(self):
        self.logger.setLevel(logging.INFO)
        myformat = logging.Formatter("Time:%(asctime)s | %(message)s")
        self.handler.setFormatter(myformat)
        self.logger.addHandler(self.handler)

    def log_with_border(self, string=None):
        if string is None:
            self.log('-' * 36)
            return

        string_size = len(string)
        dash_count = 36 - string_size
        border_dashes = dash_count // 2
        newstring = ('-' * border_dashes) + string + ('-' * border_dashes)
        self.log(newstring)

