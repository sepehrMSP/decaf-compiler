"""
Scanner for tokens
"""
from typing import List, Union, Tuple

from lark import Transformer, Lark

tokens = []
keywords = {"void", "int", "double", "bool", "string", "class", "interface", "null", "this", "extends", "implements",
            "for", "while", "if", "else", "return", "break", "new", "NewArray", "Print", "ReadInteger", "ReadLine"}

boolean = {"true", "false"}

tokens_grammar = """
    start : (INT | STRING | ID | OPERATOR | DOUBLE | DOUBLE_SCI | INLINE_COMMENT | MULTILINE_COMMENT | BRACKET)*
    ID: /[a-zA-Z][a-zA-Z0-9_]{,30}/
    INT: /0[xX][a-fA-F0-9]+/ | /[0-9]+/
    DOUBLE.2 : /(\\d)+\\.(\\d)*/
    DOUBLE_SCI.3 : /(\\d)+\\.(\\d)*[Ee][+-]?(\\d)+/
    STRING : /"[^"\\n]*"/
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
    """
    Transformer to get tokens
    """
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


def get_tokens(code: str) -> List[Tuple[str, Union[str, int, float]]]:
    """
    Scan ``code`` and returns tokens

    Args:
        code (str):

    Returns:
        list o
    """
    tokens.clear()
    parser = Lark(tokens_grammar, parser="lalr", transformer=TestTransformer())
    try:
        parser.parse(code)
    except:
        tokens.append(('UNDEFINED_TOKEN',))
    return tokens

if __name__ == '__main__':
    tokens_grammar = """
    l_value : "a" | "b"
    expr : l_value"="expr
    %import common.WS -> WHITESPACE
    %ignore WHITESPACE
    """
    print(get_tokens("""
    a = b
    """))
