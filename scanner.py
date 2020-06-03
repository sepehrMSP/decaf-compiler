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
    ID :  /([a-zA-Z])((\d)|[_a-zA-Z]){0,30}/
    INLINE_COMMENT : /\/\/.*/
    MULTILINE_COMMENT : /\/\*(\*(?!\/)|[^*])*\*\//
    %import common.WS -> WHITESPACE
    %ignore WHITESPACE
    %ignore INLINE_COMMENT
    %ignore MULTILINE_COMMENT

"""

decaf_grammar = """
    start : (decl)+
    decl : variable_decl | function_decl | class_decl | interface_decl
    variable_decl : variable";"
    variable : type ident 
    type : INT | DOUBLE | BOOL | STRING | IDENT | type "[""]" 
    function_decl : type IDENT "("formals")" stmt_block  | "void" IDENT "("formals")" stmt_block 
    formals : variable (","variable)* |  
    class_decl : "class" IDENT ("extends" IDENT)?  ("implements" IDENT (","IDENT)*)?  "{"(field)*"}" 
    field : variable_decl | function_decl 
    interface_decl : "interface" IDENT "{"(prototype)*"}" 
    prototype : type IDENT "(" formals ")" ";" | "void" IDENT "(" formals ")" ";" 
    stmt_block : "{" (variable_decl)*  (stmt)* "}" 
    stmt :  (expr)? ";" | If_stmt  | while_stmt |  for_stmt | break_stmt   | return_stmt  | print_stmt  | stmt_block 
    if_stmt : "if" "(" expr ")" stmt ("else" stmt)? 
    while_stmt      : "while" "(" expr ")" stmt 
    for_stmt : "for" "(" (expr)? ";" expr ";" (expr)? ")" stmt 
    return_stmt : "return" (expr)? ";" 
    break_stmt : "break" ";" 
    print_stmt : "Print" "(" expr (","expr)+ ")" ";" 
    expr : l_value "=" expr | constant | l_value | "this" | call | "(" expr ")" | expr "+" expr | expr "-" expr 
                    | expr "*" expr | expr "/" expr |  expr "%" expr | "-" expr | expr "<" expr | expr "<=" expr 
                    | expr ">" expr | expr ">=" expr | expr "==" expr | expr "!=" expr | expr "&&" expr | expr "||" expr
                    | "!" expr | "ReadInteger" "(" ")" |   "ReadLine" "(" ")" | "new" IDENT 
                    | "NewArray" "(" expr "," type ")" 
    l_value : IDENT |  expr  "." IDENT | expr "[" expr "]" 
    call : IDENT  "(" actuals ")" |  expr  "."  IDENT  "(" actuals ")" 
    actuals :  expr (","expr)* |  
    constant : INT | DOUBLE | DOUBLE_SCI | BOOL |  STRING | "null"
    
    DOUBLE : /(\d)+\.(\d)*/
    DOUBLE_SCI.2 : /(\d)+\.(\d)*(E|e)(( )?\+|( )?-)?( )?(\d)+/
    INT : /[0-9]+/  | /0x([a-f]|[A-F]|[0-9])+/
    BOOL.2 : "true" | "false"
    STRING : /"(?:[^\\"]|\\.)*"/
    IDENT :  /([a-zA-Z])((\d)|[_a-zA-Z]){0,30}/
    INLINE_COMMENT : /\/\/.*/
    MULTILINE_COMMENT : /\/\*(\*(?!\/)|[^*])*\*\//
    %import common.WS -> WHITESPACE
    %ignore WHITESPACE
    %ignore INLINE_COMMENT
    %ignore MULTILINE_COMMENT
"""

parser = Lark(decaf_grammar, parser="lalr")

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
    get_tokens(input())
    result_str = ""
    for token in tokens:
        if len(token) == 1:
            result_str += str(token[0])
        else:
            result_str += "{} {}".format(token[0], token[1])
        result_str += "\n"
    print(result_str)
