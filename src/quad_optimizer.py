###############################################################################
#                QUAD Code Optimizer                 #   alex.yermakov.20364  #
###############################################################################


class QUADOPtimizer(object):

    def __init__(self):
        pass

    def optimize(self, quad_code):
        optimized_code = []
        lines_to_remove = []
        jumps = []
        res = []
        idx = 0
        for line in quad_code:
            tokens = line.split()
            # Check if Jump is being performed to next line (list idx + 1 + 1 )
            if tokens[0] == 'JUMP' and tokens[1] == str(idx + 2):
                lines_to_remove.append(idx)
            # Save jump line id's to adjust later
            elif tokens[0] == 'JMPZ' or tokens[0] == 'JUMP':
                jumps.append(idx)
            # Check if we performed unnecessary allocations
            elif len(optimized_code) > 1:
                if tokens[0] == 'IASN':
                    if optimized_code[-1][0] == 'IADD' or optimized_code[-1][0] == 'ISUB' \
                            or optimized_code[-1][0] == 'IMLT' or optimized_code[-1][0] == 'IDIV':
                        if tokens[2] == optimized_code[-1][1]:
                            optimized_code[-1][1] = tokens[1]
                            lines_to_remove.append(idx)
                elif tokens[0] == 'RASN':
                    if optimized_code[-1][0] == 'RADD' or optimized_code[-1][0] == 'RSUB' \
                            or optimized_code[-1][0] == 'RMLT' or optimized_code[-1][0] == 'RDIV':
                        if tokens[2] == optimized_code[-1][1]:
                            optimized_code[-1][1] = tokens[1]
                            lines_to_remove.append(idx)
            optimized_code.append(tokens)
            idx += 1
        # Adjust jump lines when needed
        for idl in reversed(lines_to_remove):
            for idj in jumps:
                if int(optimized_code[idj][1]) >= idl + 1:
                    optimized_code[idj][1] = str(int(optimized_code[idj][1]) - 1)
        # Delete lines
        for junk in reversed(lines_to_remove):
            del optimized_code[junk]
        # Return to single string representation
        for line in optimized_code:
            res.append(' '.join(line))
        return res

