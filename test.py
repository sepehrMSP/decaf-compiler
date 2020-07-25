from lark import Lark, Transformer, Tree
from lark.visitors import Interpreter
from lark.lexer import Lexer, Token


class T(Transformer):

    def INT(self, tok):
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
    # def start(self, token):
    #     print(token , type(token))
    #     return token

    def navid(self, token):
        print()
        print(token)
        print()
        return token

    def BOOL(self, token):
        print(token + "   salam")
        print(type(token))
        return token


class NewTransformer(Transformer):
    def start(self, dard):
        # print(dard.meta)
        print(dard[0].meta)
        return Tree("start", dard)

    def section(self, kooft):
        print("section")
        print(kooft)
        print(type(kooft))
        print(self.__repr__())
        kooft[0].value = 111
        return Tree("section", kooft, [12, 2])

    def item(self, maraz):
        print("item")
        print(maraz)
        return maraz


test_parser = Lark(test_grammar, parser="lalr", transformer=TestTransformer())
test_parser2 = Lark(test_grammar2, parser="lalr")
parser2 = Lark(r"""
        start: _NL? section+
        section: "[" NAME "]" _NL item+
        item: NAME "=" VALUE? _NL -> kk1 
            | NAME "****" -> kk2
        VALUE: /./+
        %import common.CNAME -> NAME
        %import common.NEWLINE -> _NL
        %import common.WS_INLINE
        %ignore WS_INLINE
    """, parser="lalr", transformer=NewTransformer())


class TestInterpreter(Interpreter):
    def start(self, tree):
        print("oomadim too")
        print(tree.data)
        print(tree)
        # self.visit_children(tree.children)
        # self.visit(tree.children[0][1]) todo this works

    def section(self, tree):
        print("lamassab")

    def kk1(self, tree):
        print("baw too kk1 am")


if __name__ == '__main__':
    try:
        tri = parser.parse('3 14 159 if if if mmd')
    except:
        print("tamoooooooooooooooooooooooooooooooooom")

    tri2 = parser2.parse(sample_conf)
    print("\n\n\n")
    TestInterpreter().visit(tri2)
    # print(tri.children)
    # print(tri2.data)
    # print(tri2.children)
    # print()
    # print()
    print("\n\n\n")

    print(test_parser.parse('123  true how ever you far '))
