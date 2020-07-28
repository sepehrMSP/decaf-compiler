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


def cnt():
    CodeGenerator.LableCnt += 1
    return CodeGenerator.LableCnt


class CodeGenerator(Interpreter):
    current_scope = 'root'
    block_stmt_counter = 0
    str_const = 0
    LableCnt = 0

    def __init__(self):
        super().__init__()
        self.expr_types = []
        self.stmt_id = []

    def start(self, tree):
        return ''.join(self.visit_children(tree))

    def decl(self, tree):
        code = ''
        for decl in tree.children:
            if decl.data == 'variable_decl' or decl.data == 'function_decl':
                code += self.visit(decl)
        return code

    def function_decl(self, tree):
        code = ''
        if len(tree.children) == 4:
            ident = tree.children[1]
            formals = tree.children[2]
            stmt_block = tree.children[3]
        else:
            ident = tree.children[0]
            formals = tree.children[1]
            stmt_block = tree.children[2]

        if ident == 'main':
            code += (
                '.data\n'
                '   true: .asciiz "true"\n'
                '   false: .asciiz "false"\n'
                '	const10000: .double 10000.0\n'
            )
            code += ('.text\n'
                     'li $sp, 0x1002FFF8\n'
                     'main:\n')

        self.current_scope += "/" + ident.value
        code += self.visit(formals)
        self.current_scope += "/_local"
        self.current_scope += "/" + str(self.block_stmt_counter)
        self.block_stmt_counter += 1
        code += self.visit(stmt_block)
        pop_scope(self.current_scope)  # pop stmt block
        pop_scope(self.current_scope)  # pop _local
        pop_scope(self.current_scope)  # pop formals

        if ident == 'main':
            code += ('.text\n')
            code += ('\tli $v0, 10         #exit\n')
            code += ('\tsyscall\n')
        return code

    def formals(self, tree):
        return ''.join(self.visit_children(tree))

    def stmt_block(self, tree):
        code = ''
        stmt_id = cnt()
        code += ('start_stmt_{}:\n'.format(stmt_id))
        code += ''.join(self.visit_children(tree))
        code += ('end_stmt_{}:\n'.format(stmt_id))
        self.stmt_id.append(stmt_id)
        return code

    def stmt(self, tree):
        stmt_id = cnt()
        code = ''
        code += ('start_stmt_{}:\n'.format(stmt_id))
        child = tree.children[0]
        if child.data == 'if_stmt':
            code += self.visit(child)
        elif child.data == 'while_stmt':
            code += self.visit(child)
        elif child.data == 'for_stsmt':
            code += self.visit(child)
        elif child.data == 'stmt_block':
            self.current_scope += "/" + str(self.block_stmt_counter)
            self.block_stmt_counter += 1
            code += self.visit(child)
            pop_scope(self.current_scope)
        elif child.data == 'break_stmt':  # there is a problem with it !
            pass
            # call a function just for break wellformness!it should move back on the stack maybe not in this interpreter
        elif child.data == 'return_stmt':
            pass
        elif child.data == 'print_stmt':
            pass
        elif child.data == 'expr':
            code += self.visit(child)
        else:
            code += self.visit(child)
        # todo these last 4 if statements can be removed but there are here to have more explicit behavior

        code += ('end_stmt_{}:\n'.format(stmt_id))
        self.stmt_id.append(stmt_id)
        return code

    def if_stmt(self, tree):
        # return ''.join(self.visit_children(tree))

        code = ''
        print(tree.children)
        print(len(tree.children))
        code += self.visit(tree.children[0])
        then_code = self.visit(tree.children[1])
        else_code = '' if len(tree.children) == 2 else self.visit(tree.children[2])
        if len(tree.children) == 2:
            code += ("""
lw $a0, 0($sp)
addi $sp, $sp, 4
beq $a0, 0, end_stmt_{then}
j  start_stmt_{then}
            """.format(then=self.stmt_id[-1]))
            code += then_code
        else:
            code += """
lw $a0, 0($sp)
addi $sp, $sp, 4
beq $a0, 0, start_stmt_{els}
            """.format(els=self.stmt_id[-1])
            code += then_code
            code += """
j end_stmt_{els}
            """.format(els=self.stmt_id[-1])
            code += else_code
        return code

    def while_stmt(self, tree):
        return ''.join(self.visit_children(tree))

    def for_stmt(self, tree):
        return ''.join(self.visit_children(tree))

    # probably we wont need this part in cgen
    def class_decl(self, tree):
        code = ''
        ident = tree.children[0]

        if type(tree.children[1]) == lark.lexer.Token:
            pass  # it is for inheritance we scape it for now
        else:
            self.current_scope += "/__class__" + ident.value
            for field in tree.children[1:-1]:
                code += self.visit(field)
        return code

    def field(self, tree):
        return ''.join(self.visit_children(tree))

    def variable_decl(self, tree):
        code = ''
        if '/__class__' in self.current_scope:
            return code
        variable = tree.children[0]
        var_type = variable.children[0]
        if type(var_type.children[0]) != lark.lexer.Token:
            return code
        var_type = var_type.children[0].value
        if var_type not in ['int', 'double', 'bool', 'string']:
            return code
        size = 4
        if var_type == 'double':
            size = 8
        elif var_type == 'string':
            size = 256
        name = variable.children[1]
        code += ('.data\n')
        code += (self.current_scope.replace('/', '_') + '_' + name + ': .space ' + str(size) + '\n')
        return code

    def variable(self, tree):
        return ''.join(self.visit_children(tree))

    def type(self, tree):
        return ''.join(self.visit_children(tree))

    def expr(self, tree):
        return ''.join(self.visit_children(tree))

    def read_line(self, tree):
        """
        line address in stack
        """
        code = ''
        code += (""".text
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
        return code

    def read_integer(self, tree):
        code = (""".text
    li $v0, 5           #read_integer
    syscall             #ReadInteger()
    sub $sp, $sp, 4
    sw $v0, 0($sp)
""")
        self.expr_types.append(Types.INT)
        return code

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
        code = ''
        code += ''.join(self.visit_children(tree))
        code += (""".text
    lw $t0, 0($sp)
    addi $sp, $sp, 4
    li $t1, 1
    beq $t0, 0, not_{0}
        li $t1, 0
not_{0}:
    sub  $sp, $sp, 4
    sw $t1, 0($sp)
""".format(cnt()))
        self.expr_types.pop()
        self.expr_types.append(Types.BOOL)
        return code

    def neg(self, tree):
        code = ''
        code += ''.join(self.visit_children(tree))
        code += ("""
lw $a0, 0($sp)
addi $sp, $sp, 4
sub $a0, $zero, $a0
sub $sp, $sp, 4
sw $a0, 0($sp)
        """)
        return code

    def print(self, tree):
        code = ''
        for child in tree.children[0].children:
            code += self.visit(child)
            t = self.expr_types[-1]
            code += ('.text\n')
            if t == Types.DOUBLE:
                code += ("""
l.d $f12, 0($sp)
addi $sp, $sp, 8
l.d $f2, const10000
mul.d $f12, $f12, $f2
round.w.d $f12, $f12
cvt.d.w $f12, $f12
div.d $f12, $f12, $f2
li $v0, 3
syscall                
                """)
            #                 print("""
            # l.d $f12, 0($sp)
            # addi $sp, $sp, 8
            # li $v0, 3
            # syscall
            #                 """)
            elif t == Types.INT:
                code += (""".text
    li $v0, 1
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    syscall
""")
            elif t == Types.STRING:
                code += ("""
li $v0, 4
lw $a0, 0($sp)
addi $sp, $sp, 4
syscall                
                """)
                pass
            elif t == Types.BOOL:
                code += (
                    """
lw $a0, 0($sp)
addi $sp, $sp, 4
beq $a0, 0, zero_{cnt}
li $v0, 4
la $a0, true
syscall
j ezero_{cnt}
zero_{cnt}:
    li $v0, 4
    la $a0, false
    syscall
ezero_{cnt}:
""".format(cnt=cnt())
                )
        return code

    def const_int(self, tree):
        code = ''
        code += ('.text\n')
        code += ('\tli $t0, {}\n'.format(tree.children[0].value.lower()))
        code += ('\tsub $sp, $sp, 4\n')
        code += ('\tsw $t0, 0($sp)\n')
        self.expr_types.append(Types.INT)
        return code

    def const_double(self, tree):
        code = ''
        dval = tree.children[0].value.lower()
        if dval[-1] == '.':
            dval += '0'
        if '.e' in dval:
            index = dval.find('.e') + 1
            dval = dval[:index] + '0' + dval[index:]
        code += ('.text\n')
        code += ('\tli.d $f0, {}\n'.format(dval))
        code += ('\tsub $sp, $sp, 8\n')
        code += ('\ts.d $f0, 0($sp)\n')
        self.expr_types.append(Types.DOUBLE)
        return code

    def const_bool(self, tree):
        code = ''
        code += ('.text\n')
        code += ('\tli $t0, {}\n'.format(int(tree.children[0].value == 'true')))
        code += ('\tsub $sp, $sp, 4\n')
        code += ('\tsw $t0, 0($sp)\n')
        self.expr_types.append(Types.BOOL)
        return code

    def const_str(self, tree):
        code = ''
        code += ('.data\n')
        code += ('__const_str__{}: .asciiz {}\n'.format(self.str_const, tree.children[0].value))
        code += ('.text\n')
        code += '\tla $t0,'
        code += '__const_str__{}\n'.format(self.str_const)
        code += ('\tsub $sp, $sp, 4\n')
        code += ('\tsw $t0, 0($sp)\n')
        self.str_const += 1
        self.expr_types.append(Types.STRING)
        return code

    def add(self, tree):
        code = ''
        code += ''.join(self.visit_children(tree))
        code += ('.text\n')
        code += ('\tlw $t0, 0($sp)\n')
        code += ('\tlw $t1, 4($sp)\n')
        code += ('\tadd $t2, $t1, $t0\n')
        code += ('\tsw $t2, 4($sp)\n')
        code += ('\taddi $sp, $sp, 4\n')

        return code


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

    // name = ReadLine();
    // age = ReadInteger();
    
    Print(ReadInteger(), 6);
    
    arr = NewArray(5, int);

    p = new Person;
    p.setName(name);
    p.setAge(age);

    p.print();
}
"""

decaf = """
int main() {
        Print(ReadInteger(), !0, !true, 2.2, "yes_finally");
}
"""

decaf = """
int main() {
    if (true){
        Print("ok1");
    }else{
        Print("wrong1");
    }
    if (false){
        Print("wrong2");
    }else {
        Print("ok2");
    }
    if (1+2){
        Print("ok3");
    }
}
"""

"""

if (true){
    }else{
    }
    """

if __name__ == '__main__':
    parser = Lark(grammar, parser="lalr")
    parse_tree = parser.parse(decaf)
    SymbolTableMaker().visit(parse_tree)
    print(CodeGenerator().visit(parse_tree))
    pass
