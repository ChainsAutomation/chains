from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.formatter import Formatter


class FormatterSilent(Formatter):
    def main(self, result):
        return None
