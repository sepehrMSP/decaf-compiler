from lark import Lark, Transformer
from lark.lexer import Lexer, Token


class T(Transformer):

    def INT(self, tok):
        "Convert the value of `tok` from string to int, while maintaining line number & column."
        return tok.update(value=int(tok))


parser = Lark("""
start: (INT*(IF)*) | dark
dark : benz bmw
benz : BENZ
bmw : BMW
BENZ : "+"
BMW : "x"

IF: "if"
%import common.INT
%ignore " "
""", parser="lalr")

parser2 = Lark(r"""
        start: _NL? section+
        section: "[" NAME "]" _NL item+
        item: NAME "=" VALUE? _NL
        VALUE: /./+
        %import common.CNAME -> NAME
        %import common.NEWLINE -> _NL
        %import common.WS_INLINE
        %ignore WS_INLINE
    """, parser="lalr")

sample_conf = """
[bla]
a=Hello
this="that",4
empty=
"""

decaf_grammar = """
    Program ::= Decl+
    Decl ::= VariableDecl | FunctionDecl | ClassDecl | InterfaceDecl
    VariableDecl ::= Variable ;
    Variable ::= Type ident 
    Type ::= int | double | bool | string | ident | Type [] 
    FunctionDecl ::= Type ident ( Formals ) StmtBlock  | void ident ( Formals ) StmtBlock 
    Formals ::= Variable+, |  ε 
    ClassDecl ::= class ident 〈extends ident〉  〈implements ident + ,〉  { Field* } 
    Field ::= VariableDecl | FunctionDecl 
    InterfaceDecl ::= interface ident { Prototype* } 
    Prototype ::= Type ident ( Formals ) ; | void ident ( Formals ) ; 
    StmtBlock ::= { VariableDecl*  Stmt* } 
    Stmt ::=  〈Expr〉 ; | IfStmt  | WhileStmt |  ForStmt | BreakStmt   | ReturnStmt  | PrintStmt  | StmtBlock 
    IfStmt ::= if ( Expr ) Stmt 〈else Stmt〉 
    WhileStmt      ::= while ( Expr ) Stmt 
    ForStmt ::= for ( 〈Expr〉 ; Expr ; 〈Expr〉 ) Stmt 
    ReturnStmt ::= return 〈Expr〉 ; 
    BreakStmt ::= break ; 
    PrintStmt ::= Print ( Expr+, ) ; 
    Expr ::= LValue = Expr | Constant | LValue | this | Call | ( Expr ) | Expr + Expr | Expr - Expr | Expr * Expr | Expr / Expr |  Expr % Expr | - Expr | Expr < Expr | Expr <= Expr | Expr > Expr | Expr >= Expr | Expr == Expr | Expr != Expr | Expr && Expr | Expr || Expr | ! Expr | ReadInteger ( ) |   ReadLine ( ) | new ident | NewArray ( Expr , Type ) 
    LValue ::= ident |  Expr  . ident | Expr [ Expr ] 
    Call ::= ident  ( Actuals ) |  Expr  .  ident  ( Actuals ) 
    Actuals ::=  Expr+, | ε 
    Constant ::= intConstant | doubleConstant | boolConstant |  stringConstant | null
"""

test_grammar = """
    start : (INT | BOOL | STRING | ID | KEYWORD | OPERATOR | DOUBLE | DOUBLE_SCI | INLINE_COMMENT | MULTILINE_COMMENT)*
    DOUBLE : /(\d)+\.(\d)*/ 
    DOUBLE_SCI.2 : /(\d)+\.(\d)*(E|e)(( )?\+|( )?-)?( )?(\d)+/
    INT : /[0-9]+/  | /0x([a-f]|[A-F]|[0-9])+/
    BOOL.2 : "true" | "false"
    STRING : /"([a-z]|[A-Z])*"/
    KEYWORD.3 : "void"
                | " int" | " double" | " bool" | " string"
                | " class" | " interface" | " null" | " this"
                | " extends" | " implements"
                | " for" | " while" | " if" | " else" | " return" | " break"
                | " new" | " NewArray" | " Print" | " ReadInteger" | "ReadLine"

    OPERATOR : "+"
            | "-" | "*" | "/" | "%"
            | "<" | "<=" | ">" | ">=" | "=" | "==" | "!="
            | "&&" | "||" | "!" 
            | ";" | "," | "."
            | "[]" | "[" | "]" | "(" | ")" 
    ID : /([a-z]|[A-Z])((\d)|_|[a-z]|[A-Z]){0,30}/
    INLINE_COMMENT : /\/\/.*/
    MULTILINE_COMMENT : /\/\*(\*(?!\/)|[^*])*\*\//
    %import common.WS -> WHITESPACE
    %ignore WHITESPACE
    
"""

test = '123123 true mmd mmd int '

test_grammar2 = """
start : a b
a : c d
b : d c
c : IF
d : THEN
IF : "if"
THEN : "then"
%ignore " " 
%import common.NEWLINE -> _NL
"""


class TestTransformer(Transformer):
    def navid(self, token):
        print()
        print(token)
        print()
        return token

    def BOOL(self, token):
        print(token + "   salam")
        return token


test_parser = Lark(test_grammar, parser="lalr", transformer=TestTransformer())
test_parser2 = Lark(test_grammar2, parser="lalr")

if __name__ == '__main__':
    try:
        tri = parser.parse('3 14 159 if if if mmd')
    except:
        print("tamoooooooooooooooooooooooooooooooooom")

    tri2 = parser2.parse(sample_conf)
    # print(tri.children)
    print(tri2.data)
    print(tri2.children)
    print()
    print()

    print(test_parser.parse('123  true how ever you far '))
