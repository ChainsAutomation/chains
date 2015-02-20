from chains.commandline.formatter import Formatter

class FormatterGeneric(Formatter):
    def main(self, result):
        return _printResult(result).rstrip()

def _printResult(res, depth=2):
        maxDepth = 4
        s = ""
        indent = ""
        for i in range(depth):
            indent += " "
        if type(res) == type([]):
            if depth < maxDepth:
                for x in res:
                    s += _printResult(x, depth+1)
                    s += "\n"
            else:
                s += "%s%s\n" % (indent, res)
        elif type(res) == type({}):
            for k in res:
                v = res[k]
                if (type(v) == type([]) or type(v) == type({})) and depth < maxDepth:
                    v = "\n%s" % _printResult(v, depth+1)
                else:
                    v = "%s\n" % v
                s += "%s%s: %s" % (indent, k, v)
        else:
            s += "%s%s\n" % (indent, res)
        return s
