###############################################################################
#                  Error Gathering                   #   alex.yermakov.20364  #
###############################################################################

import sys


class ErrorGatherer(object):
    def __init__(self):
        self.errors = []
        self.signature = 'alex.yermakov.20364'

    def report(self, error):
        self.errors.append(error)
        print(self.signature +' | '+ error, file=sys.stderr)

    def success(self):
        return True if self.error_level() == 0 else False

    def error_level(self):
        return len(self.errors)

    def dump(self):
        return self.errors


ERR_HANDLER = ErrorGatherer()
