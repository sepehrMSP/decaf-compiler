import sys, getopt

from lark import Lark, Transformer


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('main.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
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
        # for the sake of testing :
        result_str = ""
        for token in tokens:
            if len(token) == 1:
                result_str += str(token[0])
            else:
                result_str += "{} {}".format(token[0], token[1])
            result_str += "\n"
        output_file.write(result_str)


###################################################


debug = False
tokens = []
keyword = {"void", "interface", "double", "bool", "string", "class", "int", "null", "this", "extend", "implement",
           "for",
           "while", "if", "else", "return", "break", "new", "NewArray", "Print", "ReadInteger", "ReadLine"}

grammar = """
    start : (INT | BOOL | STRING | ID | OPERATOR | DOUBLE | DOUBLE_SCI | INLINE_COMMENT | MULTILINE_COMMENT | BRACKET)*
    DOUBLE.2 : /(\d)+\.(\d)*/
    DOUBLE_SCI.3 : /(\d)+\.(\d)*(E|e)(( )?\+|( )?-)?( )?(\d)+/
    INT :    /0x([a-f]|[A-F]|[0-9])+/ | /[0-9]+/
    BOOL.2 : "true" | "false"
    STRING : /"(?:[^\\"]|\\.)*"/
    BRACKET : "{" | "}"
    OPERATOR : "+"
             | "-" | "*" | "/" | "%"
             | "<=" | "<" | ">=" | ">" | "==" | "=" | "!="
             | "&&" | "||" | "!" 
             | ";" | "," | "."
             | "[]" | "[" | "]" | "(" | ")" 
    ID : /([a-z]|[A-Z])((\d)|_|[a-z]|[A-Z]){0,30}/
    INLINE_COMMENT : /\/\/.*/
    MULTILINE_COMMENT : /\/\*(\*(?!\/)|[^*])*\*\//
    %import common.WS -> WHITESPACE
    %ignore WHITESPACE
    %ignore INLINE_COMMENT
    %ignore MULTILINE_COMMENT
"""


class TestTransformer(Transformer):
    def ID(self, token):
        if debug:
            if token in keyword:
                print(token)
                tokens.append((token.value,))
            else:
                print("T_ID", token)
                tokens.append(("T_ID", token.value))
        return token

    def BOOL(self, token):
        if debug:
            print("T_BOOLEANLITERAL", token)
        tokens.append(("T_BOOLEANLITERAL", token.value))
        return token

    def double(self, token):
        if debug:
            print("T_DOUBLELITERAL", token)
        tokens.append(("T_DOUBLELITERAL", token.value))

        return token

    DOUBLE = DOUBLE_SCI = double

    def INT(self, token):
        if debug:
            print("T_INTLITERAL", token)
        tokens.append(("T_INTLITERAL", token.value))

        return token

    def STRING(self, token):
        if debug:
            print("T_STRINGLITERAL", token)
        tokens.append(("T_STRINGLITERAL", token.value))

        return token

    def default(self, token):
        if debug:
            print(token)
        tokens.append((token.value,))
        return token

    BRACKET = OPERATOR = default


def get_tokens(code):
    tokens.clear()
    parser = Lark(grammar, parser="lalr", transformer=TestTransformer())
    result = parser.parse(code)
    if debug:
        print(result)
    return tokens


if __name__ == "__main__":
    main(sys.argv[1:])
