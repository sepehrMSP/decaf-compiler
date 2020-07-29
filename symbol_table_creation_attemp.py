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
    stmt :  (expr)? ";" | if_stmt  | while_stmt |  for_stmt | break_stmt | return_stmt | print_stmt -> print | stmt_block 
    if_stmt : "if" "(" expr ")" stmt ("else" stmt)? 
    while_stmt : "while" "(" expr ")" stmt 
    for_stmt : "for" "(" (expr)? ";" expr ";" (expr)? ")" stmt 
    return_stmt : "return" (expr)? ";" 
    break_stmt : "break" ";" 
    print_stmt : "Print" "(" expr (","expr)* ")" ";"
    expr : expr "||" expr1 -> or_bool | expr1
    expr1 : expr1 "&&" expr2 -> and_bool | expr2
    expr2 : expr2 "==" expr3 -> eq | expr2 "!=" expr3 -> ne | expr3
    expr3 : expr3 "<" expr4 -> lt | expr3 "<=" expr4 -> le | expr3 ">" expr4 -> gt | expr3 ">=" expr4 -> ge | expr4
    expr4 : expr4 "+" expr5 -> add | expr4 "-" expr5 -> sub | expr5
    expr5 : expr5 "*" expr6 -> mul | expr5 "/" expr6 -> div | expr5 "%" expr6 -> mod | expr6
    expr6 : "-" expr6 -> neg | "!" expr6 -> not_expr | expr7
    expr7 : constant | "this" | "ReadInteger" "(" ")" -> read_integer | "ReadLine" "(" ")" -> read_line | "new" IDENT | "NewArray" "(" expr "," type ")" -> new_array | "(" expr ")" | l_value | call | l_value "=" expr
    l_value : IDENT |  expr7 "." IDENT | expr7 "[" expr "]" 
    call : IDENT  "(" actuals ")" |  expr7  "."  IDENT  "(" actuals ")" 
    actuals :  expr (","expr)* |  
    constant : INT -> const_int | DOUBLE -> const_double | DOUBLE_SCI -> const_double | BOOL -> const_bool |  STRING -> const_str | "null" -> null

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

    def __eq__(self, other):
        if self.name == other.name and self.dimension == other.dimension:
            return True
        return False


class ClassType:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.variables = []
        self.functions = []
        class_type_objects.append(self)


class Function:
    def __init__(self, name=None):
        self.name = name
        self.return_type = Type()
        """formals is list of [variable_name , variable_type] maybe name part will be deleted in future"""
        self.formals = []


class SymbolTableObject:
    def __init__(self, scope=None, name=None, parent_scope=None, attribute=None):
        if attribute is None:
            attribute = []
        self.scope = scope
        self.name = name
        self.parent_scope = parent_scope
        self.type = Type()
        self.attribute = attribute
        symbol_table_objects.append(self)


symbol_table_objects = []
class_type_objects = []
function_objects = []
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
    root/Tank/f1/_local/{a number!}/a
"""
symbol_table = {}

"""class table is a hashmap of (class name) to classType object index in class_type_objects
"""
class_table = {}
"""function table is a hashmap for static functions(the functions which are not in any classes) of (function name) to 
function index in function_objects  
"""
function_table = {}

stack = ['root']


class SymbolTableMaker(Interpreter):
    symbol_table_obj_counter = 0
    class_counter = 0
    static_function_counter = 0
    """block stmt counter is a counter just for block statements during building symbol table and it differentiate
     different block statements scopes. for more details see example below:
     
     int a;
     int b;
     {
        int a;
        int c;
        {
            int d;
        }
     }
     {
        P a;
     }
     scopes are in the following order:
     
     root/a
     root/b
     root/1/a
     root/1/c
     root/2/d
     root/3/a
     """
    block_stmt_counter = 0

    def decl(self, tree):
        for declaration in tree.children:
            if declaration.data == 'variable_decl':
                # self.visit(declaration)
                pass
            elif declaration.data == 'function_decl':
                self.visit(declaration)
                pass
            elif declaration.data == 'class_decl':
                # self.visit(declaration)
                pass

    def function_decl(self, tree):
        class_type_object = tree._meta
        if len(tree.children) == 4:
            ident = tree.children[1]
            formals = tree.children[2]
            stmt_block = tree.children[3]
        else:
            ident = tree.children[0]
            formals = tree.children[1]
            stmt_block = tree.children[2]

        symbol_table_object = SymbolTableObject(scope=stack[-1], name=ident)
        symbol_table[(stack[-1], ident.value,)] = self.symbol_table_obj_counter
        self.symbol_table_obj_counter += 1

        function = Function(name=ident.value)

        if type(tree.children[0]) == lark.tree.Tree:
            object_type = tree.children[0]
            object_type._meta = symbol_table_object
            self.visit(object_type)
            function.return_type = symbol_table_object.type
        else:
            symbol_table_object.type.name = 'void'
            function.return_type.name = 'void'

        stack.append(stack[-1] + "/" + ident)
        formals._meta = function
        self.visit(formals)
        stack.append(stack[-1] + "/_local")
        stack.append(stack[-1] + "/" + str(self.block_stmt_counter))
        self.block_stmt_counter += 1
        self.visit(stmt_block)
        stack.pop()  # pop stmt block
        stack.pop()  # pop _local
        stack.pop()  # pop formals

        if class_type_object:
            class_type_object.functions.append(function)
        else:
            function_table[function.name] = self.static_function_counter
            function_objects.append(function)
            self.static_function_counter += 1

    def formals(self, tree):
        function = tree._meta
        if tree.children:
            for variable in tree.children:
                variable._meta = function
                self.visit(variable)

    def stmt_block(self, tree):
        for child in tree.children:
            if child.data == 'variable_decl':
                self.visit(child)
            else:
                self.visit(child)
                pass  # todo must complete

    def stmt(self, tree):
        child = tree.children[0]
        if child.data == 'if_stmt':
            self.visit(child)
        if child.data == 'while_stmt':
            self.visit(child)
        if child.data == 'for_stsmt':
            self.visit(child)
        if child.data == 'stmt_block':
            stack.append(stack[-1] + "/" + str(self.block_stmt_counter))
            self.block_stmt_counter += 1
            self.visit(child)
            stack.pop()
        if child.data == 'break_stmt':  # there is a problem with it !
            pass
            # call a function just for break wellformness!it should move back on the stack maybe not in this interpreter
        if child.data == 'return_stmt':
            pass
        if child.data == 'print_stmt':
            pass
        if child.data == 'expr':
            pass
        # todo these last 4 if statements can be removed but there are here to have more explicit behavior

    def if_stmt(self, tree):
        expr = tree.children[0]  # todo can be omit
        stmt = tree.children[1]
        self.visit(stmt)
        if len(tree.children) == 3:
            else_stmt = tree.children[2]
            self.visit(else_stmt)

    def while_stmt(self, tree):
        expr = tree.children[0]  # this can be omit
        stmt = tree.children[1]
        self.visit(stmt)

    def for_stmt(self, tree):
        stmt = tree.children0[-1]
        self.visit(stmt)

    def class_decl(self, tree):
        ident = tree.children[0]
        class_type_object = ClassType(name=ident)
        class_table[ident.value] = self.class_counter

        symbol_table_object = SymbolTableObject(scope=stack[-1], name=ident)
        symbol_table[(stack[-1], ident.value,)] = self.symbol_table_obj_counter
        self.symbol_table_obj_counter += 1

        if type(tree.children[1]) == lark.lexer.Token:
            pass  # it is for inheritance we scape it for now
        else:
            stack.append(stack[-1] + "/" + ident)
            for field in tree.children[1:-1]:
                field._meta = class_type_object
                self.visit(field)

    def field(self, tree):
        tree.children[0]._meta = tree._meta
        self.visit(tree.children[0])

    def variable_decl(self, tree):
        tree.children[0]._meta = tree._meta
        self.visit(tree.children[0])

    def variable(self, tree):
        object_type = tree.children[0]
        name = tree.children[1].value

        symbol_table_object = SymbolTableObject(scope=stack[-1], name=name)
        symbol_table[(stack[-1], name,)] = self.symbol_table_obj_counter
        self.symbol_table_obj_counter += 1

        object_type._meta = symbol_table_object
        self.visit(object_type)
        if type(tree._meta) == ClassType:
            class_type_object = tree._meta
            class_type_object.variables.append([name, symbol_table_object.type])
        if type(tree._meta) == Function:
            function = tree._meta
            function.formals.append([name, symbol_table_object.type])
            # note that here we can omit name from append but we assume it now for probable future use cases

    def type(self, tree):
        if type(tree.children[0]) == lark.lexer.Token:
            symbol_table_object = tree._meta
            symbol_table_object.type.name = tree.children[0].value
        else:
            symbol_table_object = tree._meta
            symbol_table_object.type.dimension += 1
            tree.children[0]._meta = tree._meta
            self.visit(tree.children[0])


text = """
int[][][] c;
int d;
void cal(int number, double mmd) {
    int c;
    {
        int d;
    }
    c = number;
}
double stone(){
    double f;
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

class_text = """

class Person {
    string name;
    int age;

    void setName(string new_name) {
        name = new_name;
    }

    void setAge(int new_age) {
        age = new_age;
    }

    void print() {
        Print("Name: ", name, " Age: ", age);
    }

}

int main() {
    Person p;

    string name;
    int age;

    name = ReadLine();
    age = ReadInteger();

    p = new Person;
    p.setName(name);
    p.setAge(age);

    p.print();
}

"""
# if __name__ == '__main__':
parser = Lark(grammar, parser="lalr")
parse_tree = parser.parse(text)
SymbolTableMaker().visit(parse_tree)
# print('****************************')
# print(stack)
# print(symbol_table)

# for checking classes
# print(class_table)
# a = class_type_objects[0].functions
# print(a[0].name, a[0].formals[0][1].name, a[1].name, a[1].return_type.name)
