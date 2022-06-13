###############################################################################
#                  I/O Handler                       #   alex.yermakov.20364  #
###############################################################################

import os

from err_handler import ERR_HANDLER


class CPQInput(object):
    def __init__(self):
        self.filename = 'default.qud'
        self.signature = ERR_HANDLER.signature

    def read_ou(self, args):
        head, tail = os.path.split(args[0])
        if len(args) < 2:
            ERR_HANDLER.report("fio: No arguments found, specify input in following format, %s <file_name>.ou" % tail)
        elif len(args) > 2:
            ERR_HANDLER.report("fio: Too many arguments, specify input in following format, %s <file_name>.ou" % tail)
        else:
            self.filename = os.path.splitext(args[1])[0] or ''
            extension = os.path.splitext(args[1])[1] or ''
            if extension != '.ou' or self.filename == '':
                ERR_HANDLER.report("fio: Incorrect file provided, check extension, should be <file_name>.ou")
            else:
                with open(args[1], 'r') as tf:
                    txt = tf.read()
                if txt:
                    return txt
                else:
                    ERR_HANDLER.report("fio: Could not read the file, might be corrupted")
                    return

    def write_qud(self, quad_commands):
        if ERR_HANDLER.success():
            self.filename = self.filename + '.qud'
            file = open(self.filename, 'w')
            for command in quad_commands:
                file.write(command + '\n')
            file.write(self.signature)
            file.close()
        else:
            self.filename = self.filename + '.dump'
            ERR_HANDLER.report(
                "qud: Compilation failed with at least %s errors, file generation halted" % ERR_HANDLER.error_level())
            ERR_HANDLER.report("dbg: Partial quad code with error log was generated at %s" % self.filename)
            file = open(self.filename, 'w')
            for command in quad_commands:
                file.write(command + '\n')
            file.write('\n' + self.signature + '\n')
            file.write('\n')
            for errors in ERR_HANDLER.dump():
                file.write(errors + '\n')
            file.close()
