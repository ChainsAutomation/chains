from chains.commandline.formatter import Formatter

class FormatterSilent(Formatter):
    def main(self, result):
        return None
