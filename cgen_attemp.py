import lark
from lark import Lark
from lark.visitors import Interpreter

from symbol_table_creation_attemp import symbol_table
from symbol_table_creation_attemp import symbol_table_objects, function_objects, \
    function_table, grammar, SymbolTableMaker, Type


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
    CodeGenerator.LabelCnt += 1
    return CodeGenerator.LabelCnt


class CodeGenerator(Interpreter):
    current_scope = 'root'
    block_stmt_counter = 0
    str_const = 0
    LabelCnt = 0

    def __init__(self):
        super().__init__()
        self.expr_types = []
        self.stmt_labels = []

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
                '.text\n'
                '__strcmp__:\n'
                '   lb $t0, 0($a0)\n'
                '   lb $t1, 0($a1)\n'
                '   bne $t0, $t1, __NE__\n'
                '   bne $t0, $zero, __cont__\n'
                '   li $v0, 1\n'
                '   jr $ra\n'
                '__cont__:\n'
                '   addi $a0, $a0, 1\n'
                '   addi $a1, $a1, 1\n'
                '   j __strcmp__\n'
                '__NE__:\n'
                '   li $v0, 0\n'
                '   jr $ra\n\n'
                '.data\n'
                '   true: .asciiz "true"\n'
                '   false: .asciiz "false"\n'
                '	const10000: .double 10000.0\n'
                '   nw: .asciiz "\\n"\n'
            )
            code += ('.text\n'
                     'main:\n')

        else:
            code += '{}:\n'.format(ident)

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
            code += '.text\n'
            code += '\tli $v0, 10         #exit\n'
            code += '\tsyscall\n'
        return code

    def formals(self, tree):
        return ''.join(self.visit_children(tree))

    def stmt_block(self, tree):
        code = ''
        stmt_id = cnt()
        store_len = len(self.stmt_labels)
        code += '.text\nstart_stmt_{}:\n'.format(stmt_id)
        for child in tree.children:
            if child.data == 'variable_decl':
                code += self.visit(child)
                variable_name = child.children[0].children[1].value
                variable_type = symbol_table_objects[symbol_table[(self.current_scope, variable_name)]].type
                if variable_type.name == 'double':
                    code += '\tl.d  $f0, {}\n'.format((self.current_scope + "/" + variable_name).replace("/", "_"))
                    code += '\taddi $sp, $sp, -8\n'
                    code += '\ts.d  $f0, 0($sp)\n'
                else:
                    code += '\tla   $t0, {}\n'.format((self.current_scope + "/" + variable_name).replace("/", "_"))
                    code += '\tlw   $t1, 0($t0)\n'
                    code += '\taddi $sp, $sp, -8\n'
                    code += '\tsw   $t1, 0($sp)\n'
            else:
                code += self.visit(child)
        # pop declared variables in this scope
        for child in reversed(tree.children):
            if child.data == 'variable_decl':
                variable_name = child.children[0].children[1].value
                variable_type = symbol_table_objects[symbol_table[(self.current_scope, variable_name)]].type
                if variable_type.name == 'double':
                    code += '\tl.d $f0, 0($sp)$\n'
                    code += '\taddi $sp, $sp, 8\n'
                    code += '\ts.d $f0 {}'.format((self.current_scope + "/" + variable_name).replace("/", "_"))
                else:
                    code += '\tlw   $t1, 0($sp)\n'
                    code += '\taddi $sp, $sp, 8\n'
                    code += '\tla   $t0, {}\n'.format((self.current_scope + "/" + variable_name).replace("/", "_"))
                    code += '\tsw   $t1, 0($t0)\n'

        # code += ''.join(self.visit_children(tree))
        code += 'end_stmt_{}:\n'.format(stmt_id)
        self.stmt_labels = self.stmt_labels[:store_len]
        self.stmt_labels.append(stmt_id)
        return code
        # todo must review by Sir Sadegh

    def stmt(self, tree):
        child = tree.children[0]
        store_len = len(self.stmt_labels)
        code = ''
        add_stmt = True if child.data not in ('while_stmt',) else False
        if add_stmt:
            stmt_id = cnt()
            code += ('start_stmt_{}:\n'.format(stmt_id))

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
            # todo put return expr to v0 ro v1 or a floating point register
            code += '\taddi $sp, $sp, -8\n'
            code += '\tsw   $ra, 0($sp)\n'
            code += '\tjr $ra\n'
            code += '\tlw   $ra, 0($sp)\n'
            code += '\taddi $sp, $sp, 8\n'
        elif child.data == 'print_stmt':
            pass
        elif child.data == 'expr':
            code += self.visit(child)
        else:
            code += self.visit(child)
        # todo these last 4 if statements can be removed but there are here to have more explicit behavior

        if add_stmt:
            code += 'end_stmt_{}:\n'.format(stmt_id)
            self.stmt_labels = self.stmt_labels[:store_len]
            self.stmt_labels.append(stmt_id)
        return code

    def if_stmt(self, tree):
        # return ''.join(self.visit_children(tree))

        code = ''
        code += self.visit(tree.children[0])
        then_code = self.visit(tree.children[1])
        else_code = '' if len(tree.children) == 2 else self.visit(tree.children[2])
        if len(tree.children) == 2:
            code += """
.text 
lw $a0, 0($sp)
addi $sp, $sp, 8
beq $a0, 0, end_stmt_{then}
j  start_stmt_{then}
""".format(then=self.stmt_labels[-1])
            code += then_code
        else:
            code += """
.text
lw $a0, 0($sp)
addi $sp, $sp, 8
beq $a0, 0, start_stmt_{els}
""".format(els=self.stmt_labels[-1])
            code += then_code
            code += """
j end_stmt_{els}
""".format(els=self.stmt_labels[-1])
            code += else_code
        return code

    def while_stmt(self, tree):
        while_id = cnt()
        store_len = len(self.stmt_labels)
        code = '.text\n'
        code += "start_stmt_{}:\n".format(while_id)
        code += self.visit(tree.children[0])
        stmt_code = self.visit(tree.children[1])
        code += """
lw $a0, 0($sp)
addi $sp, $sp, 8
beq $a0, 0, end_stmt_{while_end}
""".format(while_end=while_id)
        code += stmt_code
        code += """
j start_stmt_{while_start}
""".format(while_start=while_id)
        code += "end_stmt_{}:\n".format(while_id)
        self.stmt_labels = self.stmt_labels[:store_len]
        self.stmt_labels.append(while_id)
        return code

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
        code += '.data\n'
        code += self.current_scope.replace('/', '_') + '_' + name + ': .space ' + str(size) + '\n'
        return code

    def variable(self, tree):
        return ''.join(self.visit_children(tree))

    def type(self, tree):
        return ''.join(self.visit_children(tree))

    def expr(self, tree):
        return ''.join(self.visit_children(tree))

    def expr1(self, tree):
        return ''.join(self.visit_children(tree))

    def expr2(self, tree):
        return ''.join(self.visit_children(tree))

    def expr3(self, tree):
        return ''.join(self.visit_children(tree))

    def expr4(self, tree):
        return ''.join(self.visit_children(tree))

    def expr5(self, tree):
        return ''.join(self.visit_children(tree))

    def expr6(self, tree):
        return ''.join(self.visit_children(tree))

    def expr7(self, tree):
        child_codes = self.visit_children(tree)
        if len(child_codes) == 0:
            return ''
        return ''.join(child_codes)

    def read_line(self, tree):
        """
        line address in stack
        """
        code = ''
        code += """.text
    li $a0, 256         #Maximum string length
    li $v0, 9           #sbrk
    syscall
    sub $sp, $sp, 8
    sw $v0, 0($sp)
    move $a0, $v0
    li $a1, 256         #Maximum string length (incl. null)
    li $v0, 8           #read_string
    syscall             #ReadLine()
"""
        self.expr_types.append(Types.STRING)
        return code

    def read_integer(self, tree):
        code = """.text
    li $v0, 5           #read_integer
    syscall             #ReadInteger()
    sub $sp, $sp, 8
    sw $v0, 0($sp)
"""
        self.expr_types.append(Types.INT)
        return code

    def new_array(self, tree):
        code = ''
        code += ''.join(self.visit_children(tree))
        shamt = 2
        tp = tree.children[1].children[0]
        if type(tp) == lark.lexer.Token:
            if tp.value == Types.DOUBLE:
                shamt = 3

        code += """.text
    lw $a0, 0($sp)
    addi $sp, $sp, 8
    sll $a0, $a0, {shamt}
    li $v0, 9           #sbrk
    syscall
    sub $sp, $sp, 8
    sw $v0, 0($sp)
""".format(shamt=shamt)
        self.expr_types.append('array_{}'.format(self.expr_types.pop()))
        return code

    def not_expr(self, tree):
        code = ''.join(self.visit_children(tree))
        code += """.text
    lw $t0, 0($sp)
    addi $sp, $sp, 8
    li $t1, 1
    beq $t0, 0, not_{0}
        li $t1, 0
not_{0}:
    sub  $sp, $sp, 8
    sw $t1, 0($sp)\n
""".format(cnt())
        self.expr_types.pop()
        self.expr_types.append(Types.BOOL)
        return code

    def neg(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types[-1]
        if typ.name == 'int':
            code += """.text
    lw $t0, 0($sp)
    sub $t0, $zero, $t0
    sw $t0, 0($sp)\n
"""
        else:
            code += """.text
    l.d $f0, 0($sp)
    neg.d $f0, $f0
    s.d $f0, 0($sp)\n
"""
        return code

    def print(self, tree):
        code = ''
        for child in tree.children[0].children:
            code += self.visit(child)
            t = self.expr_types[-1]
            code += '.text\n'
            if t.name == 'double':
                code += """\tl.d $f12, 0($sp)
    addi $sp, $sp, 8
    li.d $f2, 1000.0
    mul.d $f12, $f12, $f2
    round.w.d $f12, $f12
    cvt.d.w $f12, $f12
    div.d $f12, $f12, $f2
    li $v0, 3
    syscall                

"""
            #                 print("""
            # l.d $f12, 0($sp)
            # addi $sp, $sp, 8
            # li $v0, 3
            # syscall
            #                 """)
            elif t.name == 'int':
                code += """\tli $v0, 1
    lw $a0, 0($sp)
    addi $sp, $sp, 8
    syscall\n
"""
            elif t.name == Types.STRING:
                code += """\tli $v0, 4
    lw $a0, 0($sp)
    addi $sp, $sp, 8
    syscall\n
"""
                pass
            elif t.name == 'bool' and t.dimension == 0:
                code += (
                    """\tlw $a0, 0($sp)
    addi $sp, $sp, 8
    beq $a0, 0, zero_{cnt}
    li $v0, 4
    la $a0, true
    syscall
    j ezero_{cnt}
    zero_{cnt}:
    li $v0, 4
    la $a0, false
    syscall
ezero_{cnt}:\n
""".format(cnt=cnt())
                )
        # '\n' at the end of print
        code += """
    li $v0, 4 #print new line
    la $a0, nw
    syscall\n
"""
        return code

    def const_int(self, tree):
        code = ''
        code += '.text\n'
        code += '\tli $t0, {}\n'.format(tree.children[0].value.lower())
        code += '\tsub $sp, $sp, 8\n'
        code += '\tsw $t0, 0($sp)\n\n'
        self.expr_types.append(Type('int'))
        return code

    def const_double(self, tree):
        code = ''
        dval = tree.children[0].value.lower()
        if dval[-1] == '.':
            dval += '0'
        if '.e' in dval:
            index = dval.find('.e') + 1
            dval = dval[:index] + '0' + dval[index:]
        code += '.text\n'
        code += '\tli.d $f0, {}\n'.format(dval)
        code += '\tsub $sp, $sp, 8\n'
        code += '\ts.d $f0, 0($sp)\n\n'
        self.expr_types.append(Type('double'))
        return code

    def const_bool(self, tree):
        code = ''
        code += '.text\n'
        code += '\tli $t0, {}\n'.format(int(tree.children[0].value == 'true'))
        code += '\tsub $sp, $sp, 8\n'
        code += '\tsw $t0, 0($sp)\n'
        self.expr_types.append(Type('bool'))
        return code

    def const_str(self, tree):
        code = ''
        code += '.data\n'
        code += '__const_str__{}: .asciiz {}\n'.format(self.str_const, tree.children[0].value)
        code += '.text\n'
        code += '\tla $t0, __const_str__{}\n'.format(self.str_const)
        code += '\tsub $sp, $sp, 8\n'
        code += '\tsw $t0, 0($sp)\n\n'
        self.str_const += 1
        self.expr_types.append(Type('string'))
        return code

    def add(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'int':
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tadd $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        else:
            code += '.text\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tadd.d $f4, $f2, $f0\n'
            code += '\ts.d $f4, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        return code

    def call(self, tree):
        if len(tree.children) == 3:
            # it's for class
            # todo must be done
            pass
        if len(tree.children) == 2:
            ident = tree.children[0]
            actuals = tree.children[1]
            name = ident.value
            actuals._meta = name
            self.visit(actuals)

    def actuals(self, tree):
        code = ''
        function_name = tree._meta
        function_scope = 'root/' + function_name
        actual_counter = 0
        function = function_objects[function_table[function_name]]
        # push formal parameters
        for formal in function.formals:
            formal_name = (function_scope + "/" + formal[0]).replace("/", "_")
            if formal.type.name == 'double':
                code += '\tl.d  $f0, {}\n'.format(formal_name)
                code += '\taddi $sp, $sp, -8\n'
                code += '\ts.d  $f0, 0($sp)\n'
            else:
                code += '\tla   $t0, {}\n'.format(formal_name)
                code += '\tlw   $t1, 0($t0)\n'
                code += '\taddi $sp, $sp, -8\n'
                code += '\tsw   $t1, 0($sp)\n'

        # set actual parameters to formal parameters
        for expr in tree.children:
            code += self.visit(expr)
            formal_name = function.formals[actual_counter][0]
            formal_type = function.formals[actual_counter][1].name
            if formal_type == 'double':
                # todo set a fix floating point for result of expr
                pass
            else:
                code += '\tla $t0, {}\n'.format(formal_name)
                code += '\tsw $v0, 0($t0)'
            actual_counter += 1

        code += '\tjal {}\n'.format(function_name)
        # pop formal parameters
        for formal in reversed(function.formals):
            formal_name = (function_scope + "/" + formal[0]).replace("/", "_")
            if formal.type.name == 'double':
                code += '\tl.d $f0, 0($sp)$\n'
                code += '\taddi $sp, $sp, 8\n'
                code += '\ts.d $f0 {}'.format(formal_name)
                # todo must review
            else:
                code += '\tlw   $t0, 0($sp)\n'
                code += '\taddi $sp, $sp, 8\n'
                code += '\tla   $t1, {}\n'.format(formal_name)
                code += '\tsw   $t0, 0($t1)\n'
        return code

    def sub(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'int':
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tsub $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        else:
            code += '.text\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tsub.d $f4, $f2, $f0\n'
            code += '\ts.d $f4, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        return code

    def mul(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'int':
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tmul $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        if typ.name == 'double':
            code += '.text\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tmul.d $f4, $f2, $f0\n'
            code += '\ts.d $f4, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        return code

    def div(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'int':
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tdiv $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        if typ.name == 'double':
            code += '.text\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tdiv.d $f4, $f2, $f0\n'
            code += '\ts.d $f4, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        return code

    def mod(self, tree):
        code = ''.join(self.visit_children(tree))
        code += '.text\n'
        code += '\tlw $t0, 0($sp)\n'
        code += '\tlw $t1, 8($sp)\n'
        code += '\tdiv $t1, $t0\n'
        code += '\tmfhi $t2\n'
        code += '\tsw $t2, 8($sp)\n'
        code += '\taddi $sp, $sp, 8\n'
        self.expr_types.pop()
        return code

    def le(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'int':
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tsle $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        if typ.name == 'double':
            label_cnt = cnt()
            code += '.text\n'
            code += '\tli $t0, 0\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tc.le.d $f2, $f0\n'
            code += '\tbc1f __double_le__{}\n'.format(label_cnt)
            code += '\tli $t0, 1\n'
            code += '__double_le__{}:\tsw $t0, 8($sp)\n'.format(label_cnt)
            code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
        self.expr_types.append(Type('bool'))
        return code

    def lt(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'int':
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tslt $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        if typ.name == 'double':
            label_cnt = cnt()
            code += '.text\n'
            code += '\tli $t0, 0\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tc.lt.d $f2, $f0\n'
            code += '\tbc1f __double_lt__{}\n'.format(label_cnt)
            code += '\tli $t0, 1\n'
            code += '__double_lt__{}:\tsw $t0, 8($sp)\n'.format(label_cnt)
            code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
        self.expr_types.append(Type('bool'))
        return code

    def ge(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'int':
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tsge $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        if typ.name == 'double':
            label_cnt = cnt()
            code += '.text\n'
            code += '\tli $t0, 0\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tc.lt.d $f2, $f0\n'
            code += '\tbc1t __double_lt__{}\n'.format(label_cnt)
            code += '\tli $t0, 1\n'
            code += '__double_lt__{}:\tsw $t0, 8($sp)\n'.format(label_cnt)
            code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
        self.expr_types.append(Type('bool'))
        return code

    def gt(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'int':
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tsgt $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        if typ.name == 'double':
            label_cnt = cnt()
            code += '.text\n'
            code += '\tli $t0, 0\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tc.le.d $f2, $f0\n'
            code += '\tbc1t __double_gt__{}\n'.format(label_cnt)
            code += '\tli $t0, 1\n'
            code += '__double_gt__{}:\tsw $t0, 8($sp)\n'.format(label_cnt)
            code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
        self.expr_types.append(Type('bool'))
        return code

    def eq(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'double' and typ.dimension == 0:
            label_cnt = cnt()
            code += '.text\n'
            code += '\tli $t0, 0\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tc.eq.d $f0, $f2\n'
            code += '\tbc1f __double_eq__{}\n'.format(label_cnt)
            code += '\tli $t0, 1\n'
            code += '__double_eq__{}:\tsw $t0, 8($sp)\n'.format(label_cnt)
            code += '\taddi $sp, $sp, 8\n\n'
        elif typ.name == 'string' and typ.dimension == 0:
            code += '.text\n'
            code += '\tsw $t0, -8($sp)\n'
            code += '\tsw $t1, -8($sp)\n'
            code += '\tsw $a0, -12($sp)\n'
            code += '\tsw $a1, -16($sp)\n'
            code += '\tsw $v0, -20($sp)\n'
            code += '\tsw $ra, -24($sp)\n'
            code += '\tlw $a0, 0($sp)\n'
            code += '\tlw $a1, 8($sp)\n'
            code += '\tjal __strcmp__\n'
            code += '\tsw $v0, 8($sp)\n'
            code += '\tlw $t0, -4($sp)\n'
            code += '\tlw $t1, -8($sp)\n'
            code += '\tlw $a0, -12($sp)\n'
            code += '\tlw $a1, -16($sp)\n'
            code += '\tlw $v0, -20($sp)\n'
            code += '\tlw $ra, -24($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        elif self:
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tseq $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
        self.expr_types.append(Type('bool'))
        return code

    def ne(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types.pop()
        if typ.name == 'double' and typ.dimension == 0:
            label_cnt = cnt()
            code += '.text\n'
            code += '\tli $t0, 0\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\tl.d $f2, 8($sp)\n'
            code += '\tc.eq.d $f0, $f2\n'
            code += '\tbc1t __double_ne__{}\n'.format(label_cnt)
            code += '\tli $t0, 1\n'
            code += '__double_ne__{}:\tsw $t0, 8($sp)\n'.format(label_cnt)
            code += '\taddi $sp, $sp, 8\n\n'
        elif typ.name == 'string' and typ.dimension == 0:
            code += '.text\n'
            code += '\tsw $t0, -8($sp)\n'
            code += '\tsw $t1, -8($sp)\n'
            code += '\tsw $a0, -12($sp)\n'
            code += '\tsw $a1, -16($sp)\n'
            code += '\tsw $v0, -20($sp)\n'
            code += '\tsw $ra, -24($sp)\n'
            code += '\tlw $a0, 0($sp)\n'
            code += '\tlw $a1, 8($sp)\n'
            code += '\tjal __strcmp__\n'
            code += '\tli $t0, 1\n'
            code += '\tsub $v0, $t0, $v0\n'
            code += '\tsw $v0, 8($sp)\n'
            code += '\tlw $t0, -4($sp)\n'
            code += '\tlw $t1, -8($sp)\n'
            code += '\tlw $a0, -12($sp)\n'
            code += '\tlw $a1, -16($sp)\n'
            code += '\tlw $v0, -20($sp)\n'
            code += '\tlw $ra, -24($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        elif self:
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t1, 8($sp)\n'
            code += '\tsne $t2, $t1, $t0\n'
            code += '\tsw $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
        self.expr_types.append(Type('bool'))
        return code

    def and_bool(self, tree):
        code = ''.join(self.visit_children(tree))
        code += '.text\n'
        code += '\tlw $t0, 0($sp)\n'
        code += '\tlw $t1, 8($sp)\n'
        code += '\tand $t2, $t1, $t0\n'
        code += '\tsw $t2, 8($sp)\n'
        code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
        self.expr_types.pop()
        self.expr_types.append(Type('bool'))
        return code

    def or_bool(self, tree):
        code = ''.join(self.visit_children(tree))
        code += '.text\n'
        code += '\tlw $t0, 0($sp)\n'
        code += '\tlw $t1, 8($sp)\n'
        code += '\tor $t2, $t1, $t0\n'
        code += '\tsw $t2, 8($sp)\n'
        code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
        self.expr_types.pop()
        self.expr_types.append(Type('bool'))
        return code

    def null(self, tree):
        code = '.text\n'
        code += '\tsub $sp, $sp, 4\n'
        code += '\tsw $zero, 0($sp)\n\n'
        # TODO what type should it push onto the stack?
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
    
    !((-4 < 5) && (true || (3 != 5)));
 
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
    while (false){
        Print("oj");
    }

    if (true){
        Print("ok1");
    }else{
        Print("wrong1");
    }
    
    if(true){
    }else{
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

decaf = r"""// I Guds namn
int main() {
    Print(-3.14 / 2.00);
    Print("\n", 4 * -4 / 3);
    null;
}
"""

decaf = """
int main(){
    Print("input your name:");
    Print(ReadLine());
    Print("ok bruh now input your age : ->\\n", ReadInteger(), "good age? answer is ", true);

    if (ReadInteger()){
        Print("ok1 simple if");
    }

    if (ReadInteger()){
        Print("wrong");
    }else {
        Print("eyval else ham doroste");
    }

    if (ReadInteger()){
        if(false){
            Print("wrong");
        }else{
            Print(1);
        }
        if (true){
            Print(2);
        }

        if (true){
            Print(3);
            if (false){
                Print("wrong");
            }else{
                Print(4);
                if (false){
                    Print("wrong");
                }else{
                    Print(5);
                    if (ReadInteger()){
                        Print(true);
                    }else{
                        Print(false);
                    }
                }
            }
        }else{
            Print("wrong");
        }
    }else{
        if(false){
            Print("wrong");
        }else{
            Print("wrong");
        }

        if (true){
            Print("wrong");
        }
    }
}
"""

if __name__ == '__main__':
    parser = Lark(grammar, parser="lalr")
    parse_tree = parser.parse(decaf)
    SymbolTableMaker().visit(parse_tree)
    print(CodeGenerator().visit(parse_tree))
    pass
