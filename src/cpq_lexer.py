###############################################################################
#                                   Lexer                                     #
###############################################################################

from sly import Lexer
from err_handler import ERR_HANDLER


class CPQLexer(Lexer):
    tokens = {ID, NUM,
              INPUT, OUTPUT,
              IF, ELSE, SWITCH, CASE, DEFAULT,
              WHILE, BREAK,
              INT, FLOAT, CAST,
              RELOP, ADDOP, MULOP, OR, AND, NOT}
    literals = {'(', ')', '{', '}', ',', ':', ';', '='}
    ignore_comment = r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'
    ignore = ' \t'

    def __init__(self):
        self.nesting_level = 0

    # Numbers

    @_(r'(\d*\.\d+)|(\d+\.\d*)',
       r'[0-9]+')
    def NUM(self, t):
        return t

    @_(r'static_cast<int>', r'static_cast<float>')
    def CAST(self, t):
        return t

    # Identifiers and keywords
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['input'] = INPUT
    ID['output'] = OUTPUT
    ID['if'] = IF
    ID['else'] = ELSE
    ID['switch'] = SWITCH
    ID['case'] = CASE
    ID['default'] = DEFAULT
    ID['while'] = WHILE
    ID['break'] = BREAK
    ID['int'] = INT
    ID['float'] = FLOAT

    @_(r'==', r'!=', r'>=', r'<=', r'<', r'>')
    def RELOP(self, t):
        return t

    @_(r'\+', r'\-')
    def ADDOP(self, t):
        return t

    @_(r'\*', r'\/')
    def MULOP(self, t):
        return t

    @_(r'[|]{2}')
    def OR(self, t):
        return t

    @_(r'&&')
    def AND(self, t):
        return t

    @_(r'!')
    def NOT(self, t):
        return t



    @_(r'\{')
    def lbrace(self, t):
        t.type = '{'  # Set token type to the expected literal
        self.nesting_level += 1
        return t

    @_(r'\}')
    def rbrace(self, t):
        t.type = '}'  # Set token type to the expected literal
        self.nesting_level -= 1
        return t

    # Define a rule so we can track line numbers
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        ERR_HANDLER.report("lex: Lexical error at line %s, symbol='%s'" % (self.lineno, t.value[0]))
        self.index += 1
