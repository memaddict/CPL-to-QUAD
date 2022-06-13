###############################################################################
#                    Parser                          #   alex.yermakov.20364  #
###############################################################################
import sys

from sly import Parser
from cpq_lexer import CPQLexer
from err_handler import ERR_HANDLER
from cpq_ast import *


class CPQParser(Parser):
    tokens = CPQLexer.tokens

    def __init__(self):
        pass

    # --- Declarations
    # -----------------------------------------------------------------

    @_('declarations stmt_block')
    def program(self, p):
        return ENTRYnode(p.declarations, p.stmt_block)

    @_('declarations declaration')
    def declarations(self, p):
        return DECLARATIONSnode(p.declarations, p.declaration)

    @_('epsilon')
    def declarations(self, p):
        return EPSILONnode()

    @_('idlist ":" type ";"')
    def declaration(self, p):
        return DECLARATIONnode(p.idlist, p.type, p.lineno)

    @_('INT', 'FLOAT')
    def type(self, p):
        return TYPEnode(p[0], p.lineno)

    @_('idlist "," ID')
    def idlist(self, p):
        return IDLISTnode(p.idlist, IDnode(p.ID, p.lineno), p.lineno)

    @_('ID')
    def idlist(self, p):
        return IDnode(p.ID, p.lineno)

    # --- Statements
    # -----------------------------------------------------------------

    @_('assignment_stmt', 'input_stmt', 'output_stmt', 'if_stmt', 'while_stmt', 'switch_stmt', 'break_stmt',
       'stmt_block')
    def stmt(self, p):
        return p[0]

    @_('ID "=" expression ";"')
    def assignment_stmt(self, p):
        return ASSIGNMENTnode(IDFACTORnode(p.ID, p.lineno), p.expression, p.lineno)

    @_('INPUT "(" ID ")" ";"')
    def input_stmt(self, p):
        return INPUTnode(IDFACTORnode(p.ID, p.lineno))

    @_('OUTPUT "(" expression ")" ";"')
    def output_stmt(self, p):
        return OUTPUTnode(p.expression, p.lineno)

    @_('IF "(" boolexpr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        return IFnode(p.boolexpr, p.stmt0, p.stmt1, p.lineno)

    @_('WHILE "(" boolexpr ")" stmt')
    def while_stmt(self, p):
        return WHILEnode(p.boolexpr, p.stmt, p.lineno)

    @_('SWITCH "(" expression ")" "{" caselist DEFAULT ":" stmtlist "}"')
    def switch_stmt(self, p):
        return SWITCHnode(p.expression, p.caselist, p.stmtlist, p.lineno)

    @_('caselist CASE NUM ":" stmtlist')
    def caselist(self, p):
        return CASELISTnode(p.caselist, p.NUM, p.stmtlist, p.lineno)

    @_('epsilon')
    def caselist(self, p):
        return EPSILONnode()

    @_('BREAK ";"')
    def break_stmt(self, p):
        return BREAKnode(p.lineno)

    @_('"{" stmtlist "}"')
    def stmt_block(self, p):
        return p.stmtlist

    @_('stmtlist stmt')
    def stmtlist(self, p):
        return STMTLISTnode(p.stmtlist, p.stmt)

    @_('epsilon')
    def stmtlist(self, p):
        return EPSILONnode()

    @_('boolexpr OR boolterm')
    def boolexpr(self, p):
        return BOOLEXPRnode(p.OR, p.boolexpr, p.boolterm, p.lineno)

    @_('boolterm')
    def boolexpr(self, p):
        return p.boolterm

    @_('boolterm AND boolfactor')
    def boolterm(self, p):
        return BOOLEXPRnode(p.AND, p.boolterm, p.boolfactor, p.lineno)

    @_('boolfactor')
    def boolterm(self, p):
        return p.boolfactor

    @_('NOT "(" boolexpr ")"')
    def boolfactor(self, p):
        return NOTnode(p.boolexpr, p.lineno)

    @_('expression RELOP expression')
    def boolfactor(self, p):
        return RELOPnode(p.RELOP, p.expression0, p.expression1, p.lineno)

    @_('expression ADDOP term')
    def expression(self, p):
        return OPnode(p.ADDOP, p.expression, p.term, p.lineno)

    @_('term')
    def expression(self, p):
        return p.term

    @_('term MULOP factor')
    def term(self, p):
        return OPnode(p.MULOP, p.term, p.factor, p.lineno)

    @_('factor')
    def term(self, p):
        return p.factor

    @_('"(" expression ")"')
    def factor(self, p):
        return p.expression

    @_('CAST "(" expression ")"')
    def factor(self, p):
        return CASTnode(p.CAST, p.expression, p.lineno)

    @_('ID')
    def factor(self, p):
        return IDFACTORnode(p[0], p.lineno)

    @_('NUM')
    def factor(self, p):
        return NUMFACTORnode(p[0], p.lineno)

    @_('')
    def epsilon(self, p):
        return EPSILONnode()

    # --- Errors & Recovery
    # -----------------------------------------------------------------

    def error(self, p):
        # Iterating on sly stack in reverse order
        # Trying to find last usable token with line number
        if not p:
            last_usable_line_index = -1
            while 'lineno' not in dir(self.symstack[last_usable_line_index]):
                if last_usable_line_index > -len(self.symstack):
                    last_usable_line_index -= 1
                else:
                    last_usable_line_index = 0
                    break

            last_usable_line_index = self.symstack[last_usable_line_index].lineno \
                if last_usable_line_index != 0 \
                else 0

            ERR_HANDLER.report(
                "sly: Reached unexpected EOF, last parsing attempt was at line %s " % last_usable_line_index)
            return

        # Report problematic token
        ERR_HANDLER.report(
            "sly: Syntax error at line %s, token='%s'" % (p.lineno, p.type))

        # Trying to recover by skipping tokens, until potential statement closure
        skipped = []
        while True:
            tok = next(self.tokens, None)
            if tok:
                skipped.append(tok.type)
            if not tok or tok.type == ')' or tok.type == ';' or tok.type == '}':
                break
            self.errok()
        ERR_HANDLER.report(
            "sly: Recovery attempt by skipping following tokens=%s" % skipped)

        if tok:
            return tok
        else:
            ERR_HANDLER.report(
                "sly: Failed to recover, exiting")
            sys.exit()
