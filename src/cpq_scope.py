###############################################################################
#                Scope / Symbol Table                #   alex.yermakov.20364  #
###############################################################################

from collections import OrderedDict


class Scope(object):
    def __init__(self):
        self.dict = OrderedDict()
        self.vvars = [[], []]
        self.subscope = 0

    def go_in(self):
        self.subscope += 1

    def go_out(self):
        self.subscope -=1

    def in_subscope(self):
        return True if self.subscope > 0 else False

    def generate_vvar(self, typing):
        if typing == 'float':
            tname = 'tr'
            tss = 0
        else:
            tname = 'ti'
            tss = 1
        self.vvars[tss].append(tname + str(len(self.vvars[tss]) + 1))
        self.load(self.vvars[tss][len(self.vvars[tss]) - 1])
        self.declare_missing(typing)
        self.init_var(self.vvars[tss][len(self.vvars[tss]) - 1])
        return self.vvars[tss][len(self.vvars[tss]) - 1]

    def flush_temps(self):
        # in order to reuse them in another place
        self.vvars[0].clear()
        self.vvars[1].clear()

    def load(self, name):
        if name in self.dict:
            return False
        else:
            self.dict[name] = ['NO_TYPE', 0]  # type, init yes/no
            return True

    def declare_missing(self, typing):
        for var in reversed(self.dict.keys()):
            if self.dict[var][0] == 'NO_TYPE':
                self.dict[var][0] = typing
            else:
                break

    def init_var(self, var):
        if self.in_scope(var):
            self.dict[var][1] = 1

    def initialized(self, var):
        if self.in_scope(var):
            return True if self.dict[var][1] == 1 else False
        return True

    def in_scope(self, var):
        if var in self.dict:
            return True
        else:
            return False

    def get_type(self, var):
        if '.' in var:
            return 'float'
        elif self.in_scope(var):
            return self.dict[var][0]
        else:
            return 'int'

    def switch_paring(self):
        # we always use these labels to simplify switch generation
        return 'sw0', 'sw1'
