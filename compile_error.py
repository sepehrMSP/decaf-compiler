import lark
from lark import Lark
import re

grammar = """
    start : (decl)+
    decl : variable_decl | function_decl | class_decl | interface_decl
    variable_decl : variable ";"
    variable : type IDENT 
    type : TYPE | IDENT | type "[]"
    function_decl : type IDENT "("formals")" stmt_block  | "void" IDENT "("formals")" stmt_block 
    formals : variable (","variable)* |  
    class_decl : "class" IDENT ("extends" IDENT)?  ("implements" IDENT (","IDENT)*)?  "{"(field)*"}" 
    field : variable_decl | function_decl 
    interface_decl : "interface" IDENT "{"(prototype)*"}" 
    prototype : type IDENT "(" formals ")" ";" | "void" IDENT "(" formals ")" ";" 
    stmt_block : "{" (variable_decl)*  (stmt)* "}" 
    stmt :  (expr)? ";" | if_stmt  | while_stmt |  for_stmt | break_stmt   | return_stmt  | print_stmt  | stmt_block 
    if_stmt : "if" "(" expr ")" stmt ("else" stmt)? 
    while_stmt : "while" "(" expr ")" stmt 
    for_stmt : "for" "(" (expr)? ";" expr ";" (expr)? ")" stmt 
    return_stmt : "return" (expr)? ";" 
    break_stmt : "break" ";" 
    print_stmt : "Print" "(" expr (","expr)* ")" ";" 
    expr : l_value "=" expr | constant | l_value | "this" | call | "(" expr ")" | expr "+" expr | expr "-" expr 
                    | expr "*" expr | expr "/" expr |  expr "%" expr | "-" expr | expr "<=" expr | expr "<" expr  
                    | expr ">=" expr| expr ">" expr |  expr "==" expr | expr "!=" expr | expr "&&" expr | expr "||" expr
                    | "!" expr | "ReadInteger" "(" ")" |   "ReadLine" "(" ")" | "new" IDENT 
                    | "NewArray" "(" expr "," type ")" 
    l_value : IDENT |  expr  "." IDENT | expr "[" expr "]" 
    call : IDENT  "(" actuals ")" |  expr  "."  IDENT  "(" actuals ")" 
    actuals :  expr (","expr)* |  
    constant : INT | DOUBLE | DOUBLE_SCI | BOOL |  STRING | "null"

    DOUBLE.2 : /(\\d)+\\.(\\d)*/
    DOUBLE_SCI.3 : /(\\d)+\\.(\\d)*[Ee][+-]?(\\d)+/
    INT: /0[xX][a-fA-F0-9]+/ | /[0-9]+/
    BOOL : /((true)|(false))(xxxxxxxxx)*/
    TYPE : "int" | "double" | "bool" | "string"
    STRING : /"[^"\\n]*"/
    IDENT :  /(?!((true)|(false)|(void)|(int)|(double)|(bool)|(string)|(class)|(interface)|(null)|(this)|(extends)|(implements)|(for)|(while)|(if)|(else)|(return)|(break)|(new)|(NewArray)|(Print)|(ReadInteger)|(ReadLine))([^_a-zA-Z0-9]|$))[a-zA-Z][_a-zA-Z0-9]*/
    INLINE_COMMENT : "//" /[^\\n]*/ "\\n"
    MULTILINE_COMMENT : "/*" /.*?/ "*/"
    %import common.WS -> WHITESPACE
    %ignore WHITESPACE
    %ignore INLINE_COMMENT
    %ignore MULTILINE_COMMENT
"""


def syntax_error(code: str) -> str:
    """
    check compile errors
    Args:
        code (str): code to check for compile error
    Returns:
        str:
            return "NO" if there is no compile error.
            otherwise returns "YES"
    """
    try:
        id = '[a-z][a-z0-9_]*'
        r = re.findall(id, code, flags=re.IGNORECASE)
        for i in r:
            if len(i) > 31:
                return "NO"
        Lark(grammar, parser="lalr").parse(code)
    except lark.exceptions.UnexpectedToken as e:
        print(type(e))
        return "NO"

    return "YES"
