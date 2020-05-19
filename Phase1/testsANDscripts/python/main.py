import getopt
import sys

from lark import Lark, Transformer


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        # print('main.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            # print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open("tests/" + inputfile, "r") as input_file:
        # do stuff with input file
        tokens = get_tokens(input_file.read())
        pass

    with open("out/" + outputfile, "w") as output_file:
        # write result to output file. 
        result_str = ""
        for token in tokens:
            if len(token) == 1:
                result_str += str(token[0])
            else:
                result_str += "{} {}".format(token[0], token[1])
            result_str += "\n"
        output_file.write(result_str)


###################################################


tokens = []
keywords = {"void", "int", "double", "bool", "string", "class", "interface", "null", "this", "extends", "implements",
            "for", "while", "if", "else", "return", "break", "new", "NewArray", "Print", "ReadInteger", "ReadLine"}

boolean = {"true", "false"}

grammar = """
    start : (INT | STRING | ID | OPERATOR | DOUBLE | DOUBLE_SCI | INLINE_COMMENT | MULTILINE_COMMENT | BRACKET)*
    ID: /([a-zA-Z])([a-zA-Z0-9_]){,30}/
    INT: /0[xX]([a-fA-F0-9])+/ | /[0-9]+/
    DOUBLE.2 : /(\\d)+\\.(\\d)*/
    DOUBLE_SCI.3 : /(\\d)+\\.(\\d)*[Ee]([+-])?(\\d)+/
    STRING : /"(?:[^\\"]|\\.)*"/
    BRACKET : "{" | "}"
    OPERATOR : "+" | "-" | "*" | "/" | "%"
             | "<=" | "<" | ">=" | ">" | "==" | "=" | "!="
             | "&&" | "||" | "!" 
             | ";" | "," | "."
             | "[]" | "[" | "]" | "(" | ")" 
    INLINE_COMMENT : "//" /[^\\n]*/ "\\n"
    MULTILINE_COMMENT : "/*" /.*?/ "*/"
    %import common.WS -> WHITESPACE
    %ignore WHITESPACE
    %ignore INLINE_COMMENT
    %ignore MULTILINE_COMMENT
"""


class TestTransformer(Transformer):
    def ID(self, token):
        if token in keywords:
            tokens.append((token.value,))
        elif token in boolean:
            tokens.append(("T_BOOLEANLITERAL", token.value))
        else:
            tokens.append(("T_ID", token.value))
        return token

    def double(self, token):
        tokens.append(("T_DOUBLELITERAL", token.value))
        return token

    DOUBLE = DOUBLE_SCI = double

    def INT(self, token):
        tokens.append(("T_INTLITERAL", token.value))
        return token

    def STRING(self, token):
        tokens.append(("T_STRINGLITERAL", token.value))
        return token

    def default(self, token):
        tokens.append((token.value,))
        return token

    BRACKET = OPERATOR = default


def get_tokens(code):
    tokens.clear()
    parser = Lark(grammar, parser="lalr", transformer=TestTransformer())
    try:
        parser.parse(code)
    except:
        tokens.append(('UNDEFINED_TOKEN',))
    return tokens


if __name__ == "__main__":
    main(sys.argv[1:])
