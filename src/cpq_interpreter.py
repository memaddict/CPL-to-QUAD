###############################################################################
#                 Interpreter                        #   alex.yermakov.20364  #
###############################################################################

from err_handler import ERR_HANDLER
from cpq_scope import Scope


class ICommand(object):
    def __init__(self, op=None, r1=None, r2=None, r3=None):
        self.op = op or ''
        self.r1 = r1 or ''
        self.r2 = r2 or ''
        self.r3 = r3 or ''

    def __repr__(self):
        return "< %s %s %s %s>" % (self.op, self.r1, self.r2, self.r3)


class CPQInterpreter(object):
    def __init__(self):
        self.commands = []
        self.scope = Scope()
        self.vlabels = {}

    def finalize(self):
        cleaned_code = []
        for cmd in self.commands:
            if cmd.op == 'JMPZ' or cmd.op == 'JUMP':
                cmd.r1 = self.vlabels[cmd.r1]
            cleaned_code.append("%s %s %s %s" % (cmd.op, cmd.r1, cmd.r2, cmd.r3))
        return cleaned_code

    # --- Labels & Backpatching
    # -----------------------------------------------------------------

    def cmdline(self):
        return len(self.commands) + 1

    def stmt_cmdline(self):
        self.scope.flush_temps()  # reuse of temp variables
        return self.generate_label(self.cmdline())

    def else_cmdline(self):
        else_label = self.generate_label(self.cmdline())
        self.commands.append(ICommand('JUMP', else_label))
        return else_label

    def halt_cmdline(self):
        self.commands.append(ICommand('HALT'))
        return self.cmdline() - 1

    def caselist_opening_cmdline(self, var, line):
        if self.scope.get_type(var) != 'int':
            ERR_HANDLER.report("ast: Interpreter error at line %s, 'float' in caselist, variable='%s'" % (line, var))
        self.commands.append(ICommand('IEQL', self.scope.switch_paring()[0], self.scope.switch_paring()[1], var))
        else_label = self.generate_label(self.cmdline())
        self.commands.append(ICommand('JMPZ', else_label, self.scope.switch_paring()[0]))
        return else_label

    def while_start_cmdline(self):
        self.scope.go_in()
        return self.stmt_cmdline()

    def switch_start_cmdline(self, var, line):
        self.scope.go_in()
        if self.scope.get_type(var) != 'int':
            ERR_HANDLER.report(
                "ast: Interpreter error at line %s, 'float' case expression, variable='%s'" % (line, var))
        self.commands.append(ICommand('IASN', self.scope.switch_paring()[1], var))

    def generate_label(self, cmdline):
        self.vlabels[cmdline] = cmdline
        return cmdline

    def backpatch(self, labels, target):
        for label in labels:
            self.vlabels[label] = target

    # --- Symbol Table / Scope manipulation
    # -----------------------------------------------------------------

    def load_var(self, var, line):
        if not self.scope.load(var):
            ERR_HANDLER.report("ast: Interpreter error at line %s, multiple declarations, variable='%s'" % (line, var))

    def declare_vars(self, typing):
        self.scope.declare_missing(typing)

    def validate_var(self, var, line):
        if not self.scope.in_scope(var):
            ERR_HANDLER.report("ast: Interpreter error at line %s, undeclared variable, variable='%s'" % (line, var))

    # --- Processing declarations
    # -----------------------------------------------------------------

    def process_epsilon(self):
        return []

    def process_assign(self, var1, var2, line):
        var1_type = self.scope.get_type(var1)
        var2_type = self.scope.get_type(var2)
        if var1_type == 'int' and var2_type == 'float':
            ERR_HANDLER.report(
                "ast: Interpreter error at line %s, can't assign 'float' to 'int', variable='%s'" % (line, var2))
        self.scope.init_var(var1)
        opcode = 'RASN' if var1_type == 'float' else 'IASN'
        self.commands.append(ICommand(opcode, var1, var2))
        return []

    def process_output(self, var1, line):
        var1_type = self.scope.get_type(var1)
        if not self.scope.initialized(var1):
            ERR_HANDLER.report(
                "ast: Interpreter error at line %s, uninitialized variable, variable='%s'" % (line, var1))
        opcode = 'RPRT' if var1_type == 'float' else 'IPRT'
        self.commands.append(ICommand(opcode, var1))
        return []

    def process_input(self, var1):
        var1_type = self.scope.get_type(var1)
        opcode = 'RINP' if var1_type == 'float' else 'IINP'
        self.commands.append(ICommand(opcode, var1))
        return []

    # --- Processing factors
    # -----------------------------------------------------------------

    def process_cast(self, casting, var1, line):
        var1_type = self.scope.get_type(var1)
        result_type = 'float' if 'float' in casting else 'int'
        if var1_type == result_type:
            ERR_HANDLER.report("ast: Interpreter error at line %s, casting from '%s' to '%s', variable='%s'" % (
                line, result_type, var1_type, var1))
        result = self.scope.generate_vvar(result_type)
        opcode = 'ITOR' if result_type == 'float' else 'RTOI'
        self.commands.append(ICommand(opcode, result, var1))
        return result

    def process_mathop(self, operation, var1, var2, line):
        result_type = 'float' if self.scope.get_type(var1) == 'float' or self.scope.get_type(var2) == 'float' else 'int'
        type_id = 0 if result_type == 'float' else 1
        opcodes = {'+': ['RADD', 'IADD'],
                   '-': ['RSUB', 'ISUB'],
                   '*': ['RMLT', 'IMLT'],
                   '/': ['RDIV', 'IDIV']}
        result = self.scope.generate_vvar(result_type)
        self.commands.append(ICommand(opcodes[operation][type_id], result, var1, var2))
        return result

    # --- Processing expressions
    # -----------------------------------------------------------------

    def promote_itor(self, var1, var2, line):
        var1_type = self.scope.get_type(var1)
        var2_type = self.scope.get_type(var2)
        result_type = 'float' if var1_type == 'float' or var2_type == 'float' else 'int'
        casted_var1 = var1
        casted_var2 = var2
        if result_type == 'int':
            pass
        elif result_type == 'float' and var1_type == 'int':
            casted_var1 = self.process_cast('float', var1, line)
        elif result_type == 'float' and var2_type == 'int':
            casted_var2 = self.process_cast('float', var2, line)
        return casted_var1, casted_var2, result_type

    def process_relop(self, cmdline, operation, var1, var2, line):
        cvar1, cvar2, result_type = self.promote_itor(var1, var2, line)

        type_id = 0 if result_type == 'float' else 1
        opcodes = {'==': ['REQL', 'IEQL'],
                   '!=': ['RNQL', 'INQL'],
                   '<': ['RLSS', 'ILSS'],
                   '>': ['RGRT', 'IGRT'],
                   '>=': ['RLSS', 'ILSS'],
                   '<=': ['RGRT', 'IGRT']}

        result = self.scope.generate_vvar(result_type)
        self.commands.append(ICommand(opcodes[operation][type_id], result, cvar1, cvar2))
        if operation == '>=' or operation == '<=':
            self.commands.append(ICommand('ISUB', result, '1', result))

        self.commands.append(ICommand('JMPZ', cmdline, result))
        true_label = self.generate_label(self.cmdline())
        self.commands.append(ICommand('JUMP', true_label))

        return [[true_label], [cmdline]]

    def process_boolexp(self, cmdline, operation, lft, rgt, line):
        if operation == '&&':
            self.backpatch(lft[0], cmdline)
            true_list = rgt[0]
            fals_list = lft[1] + rgt[1]
        elif operation == '||':
            self.backpatch(lft[1], cmdline)
            true_list = lft[0] + rgt[0]
            fals_list = rgt[1]
        else:
            true_list = fals_list = []
        return [true_list, fals_list]

    def procces_notexp(self, bexp):
        return [bexp[1], bexp[0]]

    # --- Processing statements
    # -----------------------------------------------------------------

    def process_entry(self, entry, halt):
        self.backpatch(entry, halt)
        return self.finalize()

    def process_stmtlist(self, s1, s2, stmtline):
        self.backpatch(s1, stmtline)
        return s2

    def process_ifstmt(self, bexp, trueline, elseline, falsline, s1, s2):
        self.backpatch(bexp[0], trueline)
        self.backpatch(bexp[1], falsline)
        nextlist = s1 + s2 + [elseline]
        return nextlist

    def process_whilestmt(self, bexp, strtline, stmtline, s1):
        self.backpatch(s1, strtline)
        self.backpatch(bexp[0], stmtline)
        strtlbl = self.generate_label(self.cmdline())
        self.vlabels[strtlbl] = strtline
        self.commands.append(ICommand('JUMP', strtlbl))
        self.scope.go_out()
        return bexp[1]

    def process_caselist(self, c1, elselbl, s1, nextline):
        self.backpatch([elselbl], nextline + 1)
        true_label = self.generate_label(self.cmdline())
        self.commands.append(ICommand('JUMP', true_label))
        exits = c1 + [true_label]
        return exits

    def process_switch(self, c1, nextline):
        self.backpatch(c1, nextline)
        self.scope.go_out()
        return []

    def process_break(self, line):
        if not self.scope.in_subscope():
            ERR_HANDLER.report(
                "ast: Interpreter error at line %s, illegal 'break;' out of if/while scope" % (line))
        return []

