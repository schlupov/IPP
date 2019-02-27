import sys


class Exception:

    def __init__(self, which_message):
        self.which_message = which_message
        self.exception()

    def exception(self):
        switcher = {
            33: FormatException.message("Bad XML format"),
        }
        return switcher.get(self.which_message, "nothing")


class FormatException(Exception):

    @staticmethod
    def message(message):
        print(message, file=sys.stderr)
        exit(33)
