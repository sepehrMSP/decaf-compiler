import lark
from lark import Lark, Tree
from lark.visitors import Interpreter
from lark.lexer import Token

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
    stmt :  (expr)? ";" | if_stmt | while_stmt | for_stmt | break_stmt | return_stmt | print_stmt -> print | stmt_block 
    if_stmt : "if" "(" expr ")" stmt ("else" stmt)? 
    while_stmt : "while" "(" expr ")" stmt 
    for_stmt : "for" "(" (expr)? ";" expr ";" (expr)? ")" stmt 
    return_stmt : "return" (expr)? ";" 
    break_stmt : "break" ";" 
    print_stmt : "Print" "(" expr (","expr)* ")" ";" -> print
    expr : l_value "=" expr -> ass | expr8
    expr8 : expr8 "||" expr1 -> or_bool | expr1
    expr1 : expr1 "&&" expr2 -> and_bool | expr2
    expr2 : expr2 "==" expr3 -> eq | expr2 "!=" expr3 -> ne | expr3
    expr3 : expr3 "<" expr4 -> lt | expr3 "<=" expr4 -> le | expr3 ">" expr4 -> gt | expr3 ">=" expr4 -> ge | expr4
    expr4 : expr4 "+" expr5 -> add | expr4 "-" expr5 -> sub | expr5
    expr5 : expr5 "*" expr6 -> mul | expr5 "/" expr6 -> div | expr5 "%" expr6 -> mod | expr6
    expr6 : "-" expr6 -> neg | "!" expr6 -> not_expr | expr7
    expr7 : constant | "ReadInteger" "(" ")" -> read_integer | "ReadLine" "(" ")" -> read_line | "new" IDENT -> class_inst | "NewArray" "(" expr "," type ")" -> new_array | "(" expr ")" | l_value -> val | call
    l_value : IDENT -> var_addr |  expr7 "." IDENT -> var_access | expr7 "[" expr "]" -> subscript
    call : IDENT  "(" actuals ")" |  expr7  "."  IDENT  "(" actuals ")" -> method
    actuals :  expr (","expr)* |  
    constant : INT -> const_int | DOUBLE -> const_double | DOUBLE_SCI -> const_double | BOOL -> const_bool |  STRING -> const_str | "null" -> null

    DOUBLE.2 : /(\\d)+\\.(\\d)*/
    DOUBLE_SCI.3 : /(\\d)+\\.(\\d)*[Ee][+-]?(\\d)+/
    INT: /0[xX][a-fA-F0-9]+/ | /[0-9]+/
    BOOL : /((true)|(false))(xabc1235ll)*/
    TYPE : "int" | "double" | "bool" | "string"
    STRING : /"[^"\\n]*"/
    IDENT :  /(?!((true)|(false)|(void)|(int)|(double)|(bool)|(string)|(class)|(interface)|(null)|(extends)|(implements)|(for)|(while)|(if)|(else)|(return)|(break)|(new)|(NewArray)|(Print)|(ReadInteger)|(ReadLine))([^_a-zA-Z0-9]|$))[a-zA-Z][_a-zA-Z0-9]*/
    INLINE_COMMENT : "//" /[^\\n]*/ "\\n"
    MULTILINE_COMMENT : "/*" /(\\n|.)*?/ "*/"
    %import common.WS -> WHITESPACE
    %ignore WHITESPACE
    %ignore INLINE_COMMENT
    %ignore MULTILINE_COMMENT
"""


class Type:
    def __init__(self, name=None, meta=None, dimension=0):
        self.name = name
        self.dimension = dimension
        self._meta = meta

    def reset(self):
        self.name = None
        self.dimension = 0
        self._meta = None

    def __eq__(self, other):
        if self.name == other.name and self.dimension == other.dimension:
            return True
        return False

    def __str__(self):
        return 'Name: {}\tDimension: {}'.format(self.name, self.dimension)


class ClassType:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        self.variables = []
        self.functions = []
        class_type_objects.append(self)

    def print_functions(self):
        l = []
        for function in self.functions:
            l.append(function.exact_name)
        # print(l)
        return

    def find_var_index(self, ident):
        counter = 0
        for var in self.variables:
            if var[0] == ident:
                return counter
            else:
                counter += 1
        return -1

    def find_var_type(self, ident):
        return self.variables[self.find_var_index(ident)][1]

    def find_function(self, name):
        for func in self.functions:
            if func.name == name:
                return func
        raise Exception("function not found")

    def find_function_index(self, name):
        counter = 0
        for func in self.functions:
            if func.name == name:
                return counter
            counter += 1
        raise Exception("function not found")

    def set_vtable(self):
        pass
        # return pointer

    def set_obj(self):
        vtable_pointer = self.set_vtable()

        pass


class Function:
    def __init__(self, name=None, exact_name=None):
        self.name = name
        self.return_type = Type()
        """formals is list of [variable_name , variable_type] maybe name part will be deleted in future"""
        self.formals = []
        """this name is scope of function which will be it's label in mips code"""
        self.exact_name = exact_name

    def set_return_type(self, return_type: Type):
        self.return_type = return_type
        return self

    def set_formals(self, formals):
        self.formals = formals
        return self

    def find_formal(self, name: str):
        counter = 0
        for formal in self.formals:
            if formal[0] == name:
                return formal, counter
            counter += 1
        raise ChildProcessError("We're doomed")


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

    def __str__(self):
        return self.name + ': ' + str(self.type.name) + ' ' + str(self.type.dimension)

    def __repr__(self):
        return self.__str__()


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
    root/__class__Tank
    root/__class__Tank/val
    root/__class__Tank/f1/a
    root/__class__Tank/f1/b
    root/__class__Tank/f1/c
    root/__class__Tank/f1/_local/{a number!}/a
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
parent_classes = []


def init():
    function_objects.append(
        Function(name='itod', exact_name='root/itod').set_return_type(
            Type('double')
        ).set_formals(
            [['ival', Type('int')]]
        )
    )

    function_table['itod'] = 0

    function_objects.append(
        Function(name='dtoi', exact_name='root/dtoi').set_return_type(
            Type('int')
        ).set_formals(
            [['dval', Type('double')]]
        )
    )

    function_table['dtoi'] = 1

    function_objects.append(
        Function(name='itob', exact_name='root/itob').set_return_type(
            Type('bool')
        ).set_formals(
            [['ival', Type('int')]]
        )
    )

    function_table['itob'] = 2

    function_objects.append(
        Function(name='btoi', exact_name='root/btoi').set_return_type(
            Type('int')
        ).set_formals(
            [['bval', Type('bool')]]
        )
    )

    function_table['btoi'] = 3

    function_objects.append(
        Function(name='ceil__', exact_name='root/ceil__').set_return_type(
            Type('int')
        ).set_formals(
            [['dval', Type('double')]]
        )
    )

    function_table['ceil__'] = 4

    # function_objects.append(
    #     Function(name='print_double__', exact_name='root/print_double__').set_return_type(
    #         Type('void')
    #     ).set_formals(
    #         [['x', Type('double')]]
    #     )
    # )
    #
    # function_table['print_double__'] = 5


init()


class SymbolTableMaker(Interpreter):
    symbol_table_obj_counter = 0
    class_counter = 0
    static_function_counter = len(function_table)
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
                self.visit(declaration)
            elif declaration.data == 'function_decl':
                self.visit(declaration)
                pass
            elif declaration.data == 'class_decl':
                self.visit(declaration)
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
        # print(stack[-1] + "/" + ident.value)
        function = Function(name=ident.value, exact_name=stack[-1] + "/" + ident.value)

        if type(tree.children[0]) == lark.tree.Tree:
            object_type = tree.children[0]
            object_type._meta = symbol_table_object
            self.visit(object_type)
            function.return_type = symbol_table_object.type
        else:
            symbol_table_object.type.name = 'void'
            function.return_type.name = 'void'

        if class_type_object:
            this = Tree(data='variable',
                        children=[Tree(data='type', children=[Token(type_='TYPE', value=class_type_object.name)]),
                                  Token(type_='IDENT', value='this')])
            temp = formals.children.copy()
            formals.children = [this] + temp

        stack.append(stack[-1] + "/" + ident)
        formals._meta = function
        self.visit(formals)
        stack.append(stack[-1] + "/_local")
        self.visit(stmt_block)
        stack.pop()  # pop _local
        stack.pop()  # pop formals

        if class_type_object:
            # temp = function.formals.copy()
            # function.formals = [['__this__', Type(name=class_type_object.name)]] + temp
            class_type_object.functions.append(function)
            pass
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
        stack.append(stack[-1] + "/" + str(self.block_stmt_counter))
        self.block_stmt_counter += 1
        for child in tree.children:
            if child.data == 'variable_decl':
                self.visit(child)
            else:
                self.visit(child)
                pass  # todo must complete
        stack.pop()

    def stmt(self, tree):
        child = tree.children[0]
        if child.data == 'if_stmt':
            self.visit(child)
        if child.data == 'while_stmt':
            self.visit(child)
        if child.data == 'for_stmt':
            self.visit(child)
        if child.data == 'stmt_block':
            self.visit(child)
        if child.data == 'break_stmt':  # there is a problem with it !
            pass
            # call a function just for break wellformness!it should move back on the stack maybe not in this interpreter
        if child.data == 'return_stmt':
            pass
        if child.data == 'print_stmt' or child.data == 'print':
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
        stmt = tree.children[-1]
        self.visit(stmt)

    def class_decl(self, tree):
        ident = tree.children[0]
        class_type_object = ClassType(name=ident)
        class_table[ident.value] = self.class_counter
        self.class_counter += 1
        symbol_table_object = SymbolTableObject(scope=stack[-1], name=ident)
        symbol_table[(stack[-1], ident.value,)] = self.symbol_table_obj_counter
        self.symbol_table_obj_counter += 1
        if len(tree.children) > 1:
            if type(tree.children[1]) == lark.lexer.Token:
                stack.append(stack[-1] + "/__class__" + ident)
                for field in tree.children[2:]:
                    field._meta = class_type_object
                    self.visit(field)
                stack.pop()
            else:
                stack.append(stack[-1] + "/__class__" + ident)
                for field in tree.children[1:]:
                    field._meta = class_type_object
                    self.visit(field)
                stack.pop()

    def field(self, tree):
        tree.children[0]._meta = tree._meta
        self.visit(tree.children[0])

    def variable_decl(self, tree):
        # todo check globals
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


class ClassTreeSetter(Interpreter):
    def decl(self, tree):
        for declaration in tree.children:
            if declaration.data == 'class_decl':
                self.visit(declaration)

    def class_decl(self, tree):
        ident = tree.children[0]

        if type(tree.children[1]) == lark.lexer.Token:
            parent_name = tree.children[1].value
            parent = class_type_objects[class_table[parent_name]]
            parent.children.append(ident.value)
        else:
            parent_classes.append(ident.value)


def set_inheritance_tree(parent_class: ClassType):
    if parent_class.children:
        for child in parent_class.children:
            child_class = class_type_objects[class_table[child]]
            child_class.variables = parent_class.variables + child_class.variables

            child_functions = child_class.functions.copy()
            child_class.functions = parent_class.functions.copy()
            parent_class_function_names = set()
            for func in parent_class.functions:
                parent_class_function_names.add(func.name)

            for func in child_functions:
                for i in range(len(child_class.functions)):
                    if child_class.functions[i].name == func.name:
                        child_class.functions[i] = func

            for func in child_functions:
                if func.name not in parent_class_function_names:
                    child_class.functions.append(func)

            set_inheritance_tree(child_class)


def set_inheritance():
    for class_name in parent_classes:
        class_object = class_type_objects[class_table[class_name]]
        set_inheritance_tree(class_object)


class ImplicitThis(Interpreter):
    def decl(self, tree):
        for child in tree.children:
            if child.data == 'class_decl':
                self.visit(child)

    def class_decl(self, tree):
        for child in tree.children:
            if type(child) != lark.lexer.Token:
                child._meta = tree.children[0].value
                self.visit(child)

    def field(self, tree):
        if tree.children[0].data == 'function_decl':
            tree.children[0]._meta = tree._meta
            self.visit(tree.children[0])

    def function_decl(self, tree):
        tree.children[-1]._meta = tree._meta
        self.visit(tree.children[-1])

    def stmt_block(self, tree):
        for child in tree.children:
            if child.data != 'variable_decl':
                child._meta = tree._meta
                self.visit(child)

    def stmt(self, tree):
        for child in tree.children:
            if child.data != 'break_stmt':
                child._meta = tree._meta
                self.visit(child)

    def if_stmt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def while_stmt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def for_stmt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def return_stmt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def print(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr(self, tree):
        tree.children[-1]._meta = tree._meta
        self.visit(tree.children[-1])

    def expr1(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr2(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr3(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr4(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr5(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr6(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr7(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr8(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def call(self, tree):
        if len(tree.children) == 2:
            name = tree._meta
            fun_name = tree.children[0].value
            exists = False
            for fun in class_type_objects[class_table[name]].functions:
                if fun.name == fun_name:
                    exists = True
            if exists:
                copy = tree.children.copy()
                this = Tree(data='val', children=[Tree(data='var_addr', children=[Token(type_='IDENT', value='this')])])
                tree.children = [this] + copy

    def ass(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def or_bool(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def and_bool(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def eq(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def ne(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def lt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def le(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def gt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def ge(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def add(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def sub(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def mul(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def div(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def mod(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def neg(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def not_expr(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def new_array(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def l_value(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def val(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def var_access(self, tree):
        tree.children[0]._meta = tree._meta
        self.visit(tree.children[0])

    def subscript(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)


just_class = """class Person{
    double name;
    int a;
    string l;
    int mmd(){
        int c;
    }
}"""
text = """
int[][][] c;
int d;
class Ostad extends Emp{
    void daneshjoo(){
    }
}
class Person{
    double name;
    int a;
    string l;
    int mmd(){
        int c;
    }
}

class Emp extends Person {
    int lks;
    int fight(){}
    int mmd(){}
} 
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

decaf = """
class Sepehr extends Person {
}

class Person {
    int age;
    double[][][][] mmd;
    double grade;
    string name;
    
    void fuck() {
        Print("i am fucking");
        a || b;
        break;
        f();
        f.g();
        gg();
        a - gggvv();
    }
}

int main() {
    Person p;
    p = new Sepehr;
    Print("akeysh");
    p.fuck();
    return 99;
    ;;;;;
}
"""

if __name__ == '__main__':
    parser = Lark(grammar, parser="lalr")
    parse_tree = parser.parse(decaf)
    ImplicitThis().visit(parse_tree)
    # SymbolTableMaker().visit(parse_tree)
    # ClassTreeSetter().visit(parse_tree)
    # print(symbol_table)
    # set_inheritance()
    # for x in class_type_objects[0].functions:
    #     print(x.exact_name)
    # class_type_objects[1].print_functions()
# print('****************************')
# print(stack)
# print(symbol_table)

# for checking classes
# print(class_table)
# a = class_type_objects[0].functions
# print(a[0].name, a[0].formals[0][1].name, a[1].name, a[1].return_type.name)
