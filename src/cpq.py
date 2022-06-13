###############################################################################
#                  Python CPQ                         #  alex.yermakov.20364  #
###############################################################################

import sys

from cpq_lexer import CPQLexer
from cpq_parser import CPQParser
from cpq_io_handler import CPQInput
from quad_optimizer import QUADOPtimizer

if __name__ == '__main__':
    io = CPQInput()
    lexer = CPQLexer()
    parser = CPQParser()
    optimizer = QUADOPtimizer()

    ou_file = io.read_ou(sys.argv)
    if ou_file:
        ast = parser.parse(lexer.tokenize(ou_file))
        code = ast.interpret()
        final = optimizer.optimize(code)
        io.write_qud(final)

