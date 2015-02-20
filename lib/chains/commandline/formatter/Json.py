from chains.commandline.formatter import Formatter
import chains.common.jsonlib as json

class FormatterJson(Formatter):
    def main(self, result):
        return json.encode(result)
