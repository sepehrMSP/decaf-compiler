from lark import Lark

grammar = """
    start : (decl)+
    decl : variable_decl | function_decl | class_decl | interface_decl
    variable_decl : variable ";"
    variable : type IDENT 
    type : "int" | "double" | "bool" | "string" | IDENT | type "[]"
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


def syntax_error(code: str) -> 'str':
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
        Lark(grammar, parser="lalr").parse(code)
    except Exception as e:
        print(type(e))
        return "YES"

    return "NO"
