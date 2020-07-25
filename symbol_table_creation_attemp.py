import lark
from lark import Lark
from lark.visitors import Interpreter
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
    BOOL : /((true)|(false))(xabc1235ll)*/
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


class Type:
    def __init__(self, name=None, meta=None):
        self.name = name
        self.dimension = 0
        self._meta = meta

    def reset(self):
        self.name = None
        self.dimension = 0
        self._meta = None


class ClassType(Type):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.functions = None
        self.fields = None


class SymbolTableObject:
    def __init__(self, scope=None, name=None, parent_scope=None, type=Type(), value=None, attribute=[]):
        self.scope = scope
        self.name = name
        self.parent_scope = parent_scope
        self.type = type
        self.value = value
        self.attribute = attribute
        symbol_table_objects.append(self)


symbol_table_objects = []
""" symbol table is a hashmap with keys of (scope,name)
scope convension is something like directories; for example see below:

Class Tank:
    double val;
    function f1(int a , int b, int c):
        double a = 5;

scopes are in the following way:
    root/Tank
    root/Tank/val
    root/Tank/f1/a
    root/Tank/f1/b
    root/Tank/f1/c
    root/Tank/f1/_local/a
"""
symbol_table = {}

stack = ['root']


class SymbolTableMaker(Interpreter):
    symbol_table_obj_counter = 0

    def decl(self, tree):
        for declaration in tree.children:
            if declaration.data == 'variable_decl':
                # self.visit(declaration)
                pass
            elif declaration.data == 'function_decl':
                self.visit(declaration)
            elif declaration == 'class_decl':
                pass

    def function_decl(self, tree):
        if len(tree.children) == 4:
            ident = tree.children[1]
            formals = tree.children[2]
            stmt_block = tree.children[3]
        else:
            ident = tree.children[0]
            formals = tree.children[1]
            stmt_block = tree.children[2]

        symbol_table_object = SymbolTableObject(scope=stack[-1], name=ident)
        symbol_table[(stack[-1], ident,)] = self.symbol_table_obj_counter
        self.symbol_table_obj_counter += 1

        if type(tree.children[0]) == lark.tree.Tree:
            object_type = tree.children[0]
            object_type._meta = symbol_table_object
            self.visit(object_type)
        else:
            symbol_table_object.type = 'void'

        stack.append(stack[-1] + "/" + ident)
        self.visit(formals)
        stack.append(stack[-1] + "/_local")
        self.visit(stmt_block)
        stack.pop()
        stack.pop()

    def formals(self, tree):
        if tree.children:
            for variable in tree.children:
                self.visit(variable)

    def stmt_block(self, tree):
        print(tree.children)
        for child in tree.children:
            if child.data == 'variable_decl':
                self.visit(child)
            else:
                pass

    def variable_decl(self, tree):
        self.visit(tree.children[0])

    def variable(self, tree):
        object_type = tree.children[0]
        name = tree.children[1].value
        symbol_table_obj = SymbolTableObject(scope=stack[-1], name=name)
        symbol_table[(stack[-1], name,)] = self.symbol_table_obj_counter
        self.symbol_table_obj_counter += 1
        object_type._meta = symbol_table_obj
        self.visit(object_type)

    def type(self, tree):
        if type(tree.children[0]) == lark.lexer.Token:
            obj = tree._meta
            obj.type.name = tree.children[0].value
        else:
            obj = tree._meta
            obj.type.dimension += 1
            tree.children[0]._meta = obj
            self.visit(tree.children[0])


text = """
int[][][] c;
int d;
void cal(int number, double mmd) {
    int c;
    c = number;
}
int main() {
    int a;
    int b;

    a = ReadInteger();
    b = ReadInteger();

    Print(a);
    Print(b);
}

"""
if __name__ == '__main__':
    parser = Lark(grammar, parser="lalr")
    parse_tree = parser.parse(text)
    SymbolTableMaker().visit(parse_tree)
    print('****************************')
    print(stack)
    print(symbol_table)
    print(symbol_table_objects[0].type)
