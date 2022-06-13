###############################################################################
#                     AST                            #   alex.yermakov.20364  #
###############################################################################

from abc import ABCMeta, abstractmethod

from cpq_interpreter import CPQInterpreter

ASTInterpreter = CPQInterpreter()  # Not imported further


# --------------------------------------------------------------------------
# --- Objects related to entry / initialization
# --------------------------------------------------------------------------

class CPQAST(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def interpret(self):
        pass


class ENTRYnode(CPQAST):
    def __init__(self, declaration, statements):
        self.declaration = declaration
        self.statements = statements

    def interpret(self):
        self.declaration.interpret()
        s1 = self.statements.interpret()
        ext = ASTInterpreter.halt_cmdline()
        return ASTInterpreter.process_entry(s1, ext)


# --------------------------------------------------------------------------
# --- Objects related to declaration
# --------------------------------------------------------------------------

class DECLARATIONSnode(CPQAST):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def interpret(self):
        self.left.interpret()
        self.right.interpret()


class DECLARATIONnode(CPQAST):
    def __init__(self, idlist, typing, line):
        self.idlist = idlist
        self.typing = typing
        self.line = line

    def interpret(self):
        self.idlist.interpret()
        self.typing.interpret()


class EPSILONnode(CPQAST):
    def __init__(self):
        pass

    def interpret(self):
        return ASTInterpreter.process_epsilon()


class TYPEnode(CPQAST):
    def __init__(self, typing, line):
        self.typing = typing
        self.line = line

    def interpret(self):
        ASTInterpreter.declare_vars(self.typing)


class IDLISTnode(CPQAST):
    def __init__(self, left, right, line):
        self.left = left
        self.right = right
        self.line = line

    def interpret(self):
        self.left.interpret()
        self.right.interpret()


class IDnode(CPQAST):
    def __init__(self, rid, line):
        self.id = rid
        self.line = line

    def interpret(self):
        ASTInterpreter.load_var(self.id, self.line)


# --------------------------------------------------------------------------
# --- Objects related to statements
# --------------------------------------------------------------------------

class ASSIGNMENTnode(CPQAST):
    def __init__(self, rid, expr, line):
        self.rid = rid
        self.expr = expr
        self.line = line

    def interpret(self):
        tid = self.rid.interpret()
        exp = self.expr.interpret()
        return ASTInterpreter.process_assign(tid, exp, self.line)


class INPUTnode(CPQAST):
    def __init__(self, rid):
        self.rid = rid

    def interpret(self):
        tid = self.rid.interpret()
        return ASTInterpreter.process_input(tid)


class OUTPUTnode(CPQAST):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line

    def interpret(self):
        exp = self.expr.interpret()
        return ASTInterpreter.process_output(exp, self.line)


class IFnode(CPQAST):
    def __init__(self, boolexpr, leftTrue, rightFalse, line):
        self.boolexpr = boolexpr
        self.leftTrue = leftTrue
        self.rightFalse = rightFalse
        self.line = line

    def interpret(self):
        bexp = self.boolexpr.interpret()
        trueline = ASTInterpreter.stmt_cmdline()
        s1 = self.leftTrue.interpret()  # S1
        elseline = ASTInterpreter.else_cmdline()
        falsline = ASTInterpreter.stmt_cmdline()
        s2 = self.rightFalse.interpret()  # S2
        return ASTInterpreter.process_ifstmt(bexp, trueline, elseline, falsline, s1, s2)


class BLOCKnode(CPQAST):
    def __init__(self, stmt):
        self.stmt = stmt

    def interpret(self):
        return self.stmt.interpret()


class WHILEnode(CPQAST):
    def __init__(self, boolexpr, stmt, line):
        self.boolexpr = boolexpr
        self.stmt = stmt
        self.line = line

    def interpret(self):
        strtline = ASTInterpreter.while_start_cmdline()
        bexp = self.boolexpr.interpret()
        stmtline = ASTInterpreter.stmt_cmdline()
        s1 = self.stmt.interpret()
        return ASTInterpreter.process_whilestmt(bexp, strtline, stmtline, s1)


class SWITCHnode(CPQAST):
    def __init__(self, expr, caselist, stmtlist, line):
        self.expr = expr
        self.caselist = caselist
        self.stmtlist = stmtlist
        self.line = line

    def interpret(self):
        e1 = self.expr.interpret()
        ASTInterpreter.switch_start_cmdline(e1, self.line)
        c1 = self.caselist.interpret()
        s1 = self.stmtlist.interpret()
        nextline = ASTInterpreter.cmdline()
        return ASTInterpreter.process_switch(c1, nextline)


class CASELISTnode(CPQAST):
    def __init__(self, caselist, num, stmtlist, line):
        self.caselist = caselist
        self.num = num
        self.stmtlist = stmtlist
        self.line = line

    def interpret(self):
        c1 = self.caselist.interpret()
        elselbl = ASTInterpreter.caselist_opening_cmdline(self.num, self.line)
        s1 = self.stmtlist.interpret()
        nextline = ASTInterpreter.cmdline()
        return ASTInterpreter.process_caselist(c1, elselbl, s1, nextline)


class BREAKnode(CPQAST):  # Kinda unused atm
    def __init__(self, line):
        self.line = line

    def interpret(self):
        return ASTInterpreter.process_break(self.line)


class STMTLISTnode(CPQAST):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def interpret(self):
        s1 = self.left.interpret()
        stmtline = ASTInterpreter.stmt_cmdline()
        s2 = self.right.interpret()
        return ASTInterpreter.process_stmtlist(s1,s2, stmtline)


# --------------------------------------------------------------------------
# --- Objects related to expressions
# --------------------------------------------------------------------------

class BOOLEXPRnode(CPQAST):
    def __init__(self, operation, left, right, line):
        self.operation = operation
        self.left = left
        self.right = right
        self.line = line

    def interpret(self):
        left_lbls = self.left.interpret()
        cmdline = ASTInterpreter.stmt_cmdline()
        rght_lbls = self.right.interpret()
        return ASTInterpreter.process_boolexp(cmdline, self.operation, left_lbls, rght_lbls, self.line)


class NOTnode(CPQAST):
    def __init__(self, bxpr, line):
        self.expr = bxpr
        self.line = line

    def interpret(self):
        return ASTInterpreter.procces_notexp(self.expr.interpret())


class RELOPnode(CPQAST):
    def __init__(self, operation, left, right, line):
        self.operation = operation
        self.left = left
        self.right = right
        self.line = line

    def interpret(self):
        relopline = ASTInterpreter.stmt_cmdline()
        lft = self.left.interpret()
        rgt = self.right.interpret()
        return ASTInterpreter.process_relop(relopline, self.operation, lft, rgt, self.line)


# --------------------------------------------------------------------------
# --- Objects related to factors
# --------------------------------------------------------------------------


class CASTnode(CPQAST):
    def __init__(self, casting, expr, line):
        self.casting = casting
        self.expr = expr
        self.line = line

    def interpret(self):
        exp = self.expr.interpret()
        res = ASTInterpreter.process_cast(self.casting, exp, self.line)
        return res


class OPnode(CPQAST):
    def __init__(self, operation, left, right, line):
        self.operation = operation
        self.left = left
        self.right = right
        self.line = line

    def interpret(self):
        lft = self.left.interpret()
        rgt = self.right.interpret()
        res = ASTInterpreter.process_mathop(self.operation, lft, rgt, self.line)
        return res


class IDFACTORnode(CPQAST):
    def __init__(self, value, line):
        self.value = value
        self.line = line

    def interpret(self):
        ASTInterpreter.validate_var(self.value, self.line)
        return self.value


class NUMFACTORnode(CPQAST):
    def __init__(self, value, line):
        self.value = value
        self.line = line

    def interpret(self):
        return self.value
