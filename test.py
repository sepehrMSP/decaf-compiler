from lark import Lark, Transformer
from lark.lexer import Lexer, Token


class T(Transformer):

    def INT(self, tok):
        "Convert the value of `tok` from string to int, while maintaining line number & column."
        return tok.update(value=int(tok))


class Tar(Lexer):
    pass


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
""", parser="lalr", transformer=T())

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
    start : (INT | BOOL | STRING | ID | KEYWORD | PUNCTUATION)*
    INT : /[0-9]+/
    BOOL.2 : "true" | "false"
    STRING : /"([a-z]|[A-Z])*"/
    KEYWORD.3 : "void" | "int" | "double"
    PUNCTUATION : "." | ";" | "[" | "]"
    ID : /([a-z]|[A-Z])+(\d)*/
    %ignore " " 
"""

test = '123123 true mmd mmd int '


class TestTransformer(Transformer):
    def INT(self, token):
        print("T_INTLITERAL " + token)
        return token


test_parser = Lark(test_grammar, parser="lalr", transformer=TestTransformer())

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
