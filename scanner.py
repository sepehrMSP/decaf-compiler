from lark import Lark, Transformer

debug = True
tokens = []
keyword = {"void" , "interface", "double", "bool", "string", "class", "int", "null", "this", "extend", "implement", "for",
           "while", "if", "else", "return", "break", "new", "NewArray", "Print", "ReadInteger", "ReadLine"}
grammar = """
    start : (INT | BOOL | STRING | ID | OPERATOR | DOUBLE | DOUBLE_SCI | INLINE_COMMENT | MULTILINE_COMMENT | BRACKET)*
    DOUBLE : /(\d)+\.(\d)*/
    DOUBLE_SCI.2 : /(\d)+\.(\d)*(E|e)(( )?\+|( )?-)?( )?(\d)+/
    INT : /[0-9]+/  | /0x([a-f]|[A-F]|[0-9])+/
    BOOL.2 : "true" | "false"
    STRING : /"(?:[^\\"]|\\.)*"/
    BRACKET : "{" | "}"
    OPERATOR : "+"
             | "-" | "*" | "/" | "%"
             | "<" | "<=" | ">" | ">=" | "==" | "=" | "!="
             | "&&" | "||" | "!" 
             | ";" | "," | "."
             | "[]" | "[" | "]" | "(" | ")" 
    ID :  /([a-z]|[A-Z])((\d)|_|[a-z]|[A-Z]){0,30}/
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
            if token.value in keyword:
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


if __name__ == "__main__":
    get_tokens(
        """
void


        """
    )
    result_str = ""
    for token in tokens:
        if len(token) == 1:
            result_str += str(token[0])
        else:
            result_str += "{} {}".format(token[0], token[1])
        result_str += "\n"
    print(result_str)
