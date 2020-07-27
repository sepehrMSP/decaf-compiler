import enum

import lark
from lark import Lark
from lark.visitors import Interpreter
from symbol_table_creation_attemp import symbol_table_objects, parse_tree, class_type_objects, function_objects, \
    class_table, function_table, grammar, SymbolTableMaker


def pop_scope(scope):
    scopes = scope.split('/')
    scopes.pop()
    parent_scope = '/'.join(scopes)
    return parent_scope


class Types:
    BOOL = 'bool'
    INT = 'int'
    STRING = 'string'
    DOUBLE = 'double'


class CodeGenerator(Interpreter):
    current_scope = 'root'
    block_stmt_counter = 0
    str_const = 0

    def __init__(self):
        super().__init__()
        self.expr_types = []

    def start(self, tree):
        self.visit_children(tree)

    def decl(self, tree):
        for decl in tree.children:
            if decl.data == 'variable_decl' or decl.data == 'function_decl':
                self.visit(decl)

    def function_decl(self, tree):
        if len(tree.children) == 4:
            ident = tree.children[1]
            formals = tree.children[2]
            stmt_block = tree.children[3]
        else:
            ident = tree.children[0]
            formals = tree.children[1]
            stmt_block = tree.children[2]

        if ident == 'main':
            print('main:\n')

        self.current_scope += "/" + ident.value
        self.visit(formals)
        self.current_scope += "/_local"
        self.current_scope += "/" + str(self.block_stmt_counter)
        self.block_stmt_counter += 1
        self.visit(stmt_block)
        pop_scope(self.current_scope)  # pop stmt block
        pop_scope(self.current_scope)  # pop _local
        pop_scope(self.current_scope)  # pop formals

        if ident == 'main':
            print('.text')
            print('\tli $v0, 10         #exit')
            print('\tsyscall')

    def formals(self, tree):
        self.visit_children(tree)

    def stmt_block(self, tree):
        self.visit_children(tree)

    def stmt(self, tree):
        child = tree.children[0]
        if child.data == 'if_stmt':
            self.visit(child)
        elif child.data == 'while_stmt':
            self.visit(child)
        elif child.data == 'for_stsmt':
            self.visit(child)
        elif child.data == 'stmt_block':
            self.current_scope += "/" + str(self.block_stmt_counter)
            self.block_stmt_counter += 1
            self.visit(child)
            pop_scope(self.current_scope)
        elif child.data == 'break_stmt':  # there is a problem with it !
            pass
            # call a function just for break wellformness!it should move back on the stack maybe not in this interpreter
        elif child.data == 'return_stmt':
            pass
        elif child.data == 'print_stmt':
            pass
        elif child.data == 'expr':
            self.visit(child)
        else:
            self.visit(child)
        # todo these last 4 if statements can be removed but there are here to have more explicit behavior

    def if_stmt(self, tree):
        self.visit_children(tree)

    def while_stmt(self, tree):
        self.visit_children(tree)

    def for_stmt(self, tree):
        self.visit_children(tree)

    # probably we wont need this part in cgen
    def class_decl(self, tree):
        ident = tree.children[0]

        if type(tree.children[1]) == lark.lexer.Token:
            pass  # it is for inheritance we scape it for now
        else:
            self.current_scope += "/__class__" + ident.value
            for field in tree.children[1:-1]:
                self.visit(field)

    def field(self, tree):
        self.visit_children(tree)

    def variable_decl(self, tree):
        if '/__class__' in self.current_scope:
            return
        variable = tree.children[0]
        var_type = variable.children[0]
        if type(var_type.children[0]) != lark.lexer.Token:
            return
        var_type = var_type.children[0].value
        if var_type not in ['int', 'double', 'bool', 'string']:
            return
        size = 4
        if var_type == 'double':
            size = 8
        elif var_type == 'string':
            size = 256
        name = variable.children[1]
        print('.data')
        print(self.current_scope.replace('/', '_') + '_' + name + ': .space ' + str(size) + '\n')

    def variable(self, tree):
        self.visit_children(tree)

    def type(self, tree):
        self.visit_children(tree)

    def expr(self, tree):
        self.visit_children(tree)

    def read_line(self, tree):
        """
        line address in stack
        """
        print(""".text
    li $a0, 256         #Maximum string length
    li $v0, 9           #sbrk
    syscall
    sub $sp, $sp, 4
    sw $v0, 0($sp)
    move $a0, $v0
    li $a1, 256         #Maximum string length (incl. null)
    li $v0, 8           #read_string
    syscall             #ReadLine()
""")
        self.expr_types.append(Types.STRING)

    def read_integer(self, tree):
        print(""".text
    li $v0, 5           #read_integer
    syscall             #ReadInteger()
    sub $sp, $sp, 4
    sw $v0, 0($sp)
""")
        self.expr_types.append(Types.INT)

    def new_array(self, tree):
        self.visit_children(tree)
        print(""".text
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    sll $a0, $a0, {shamt}
    li $v0, 9           #sbrk
    syscall
    sub $sp, $sp, 4
    sw $v0, 0($sp)
""".format(shamt="3" if self.expr_types[-1] == Types.DOUBLE else '2'))
        self.expr_types.append('array_{}'.format(self.expr_types.pop()))

    def not_expr(self, tree):
        self.visit_children(tree)
        print(""".text
    lw $t0, 0($sp)
    addi $sp, $sp, 4
    li $t1, 0
    beq $t0, 0, not_
        li $t1, 1
not_:
    sub  $sp, $sp, 4
    sw $t1, 0($sp)
""")
        self.expr_types.pop()
        self.expr_types.append(Types.BOOL)

    # def print(self, tree):
    #     self.visit_children(tree)
    #     for child in tree.children:
    #         print(child)
    #     pass

    def const_int(self, tree):
        print('.text')
        print('\tli $t0,', tree.children[0].value.lower())
        print('\tsub $sp, $sp, 4')
        print('\tsw $t0, 0($sp)\n')
        self.expr_types.append(Types.INT)

    def const_double(self, tree):
        dval = tree.children[0].value.lower()
        if dval[-1] == '.':
            dval += '0'
        if '.e' in dval:
            index = dval.find('.e') + 1
            dval = dval[:index] + '0' + dval[index:]
        print('.text')
        print('\tli.d $f0, {}'.format(dval))
        print('\tsub $sp, $sp, 8')
        print('\ts.d $f0, 0($sp)\n')
        self.expr_types.append(Types.DOUBLE)

    def const_bool(self, tree):
        print('.text')
        print('\tli $t0,', int(tree.children[0].value == 'true'))
        print('\tsub $sp, $sp, 4')
        print('\tsw $t0, 0($sp)\n')
        self.expr_types.append(Types.BOOL)

    def const_str(self, tree):
        print('.data')
        print('__const_str__{}: .asciiz {}\n'.format(self.str_const, tree.children[0].value))
        print('.text')
        print('\tla $t0,', '__const_str__{}'.format(self.str_const))
        print('\tsub $sp, $sp, 4')
        print('\tsw $t0, 0($sp)\n')
        self.str_const += 1
        self.expr_types.append(Types.STRING)

    def add(self, tree):
        self.visit_children(tree)
        print('.text')
        print('\tlw $t0, 0($sp)')
        print('\tlw $t1, 4($sp)')
        print('\tadd $t2, $t1, $t0')
        print('\tsw $t2, 4($sp)')
        print('\taddi $sp, $sp, 4\n')


decaf = """
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
    
    (3);
    
    4 + 5;

    name = ReadLine();
    age = ReadInteger();
    
    arr = NewArray(5, int);

    p = new Person;
    p.setName(name);
    p.setAge(age);

    p.print();
}
"""

# decaf = """
# int main() {
#     b = NewArray(5, double);
#     a = ReadInteger();
#     Print(5, "6");
# }
# """

if __name__ == '__main__':
    parser = Lark(grammar, parser="lalr")
    parse_tree = parser.parse(decaf)
    SymbolTableMaker().visit(parse_tree)
    CodeGenerator().visit(parse_tree)
    pass
