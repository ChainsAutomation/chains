from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.formatter import Formatter
import chains.common.jsonlib as json


class FormatterJson(Formatter):
    def main(self, result):
        return json.encode(result)
