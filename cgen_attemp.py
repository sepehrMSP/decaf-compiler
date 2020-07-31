from copy import deepcopy
import lark
from lark import Lark
from lark.visitors import Interpreter

from symbol_table_creation_attemp import symbol_table, text, just_class, set_inheritance, ClassTreeSetter
from symbol_table_creation_attemp import symbol_table_objects, function_objects, \
    function_table, grammar, SymbolTableMaker, Type


def pop_scope(scope):
    scopes = scope.split('/')
    scopes.pop()
    parent_scope = '/'.join(scopes)
    return parent_scope


def tab(code) -> str:
    codes = code.split('\n')
    if len(codes[0]) == 0:
        codes = codes[1:]
    remove = 0
    for char in codes[0]:
        if char == ' ':
            remove += 1
        else:
            break
    for i in range(len(codes)):
        codes[i] += '\n'
        line = codes[i]
        if line[:remove] == ' ' * remove:
            codes[i] = line[remove:]
    if codes[-1][-1] != '\n':
        codes[-1][-1] += '\n'
    return ''.join(codes)


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
    """we need a way to store which local_variable do we have in our current scope so that in case of recursive
    call save the prior values of local_vars. protocol of this stack is in the following order:
    - in the entering of a stmt_block we push every variable_decl consist of [full scope name, type]
    - in the exiting of a stmt_block we pop last N elements which N is the number of variable_decl in that stmt_block
    - before return which is equivalent to 'jr $ra', we pop last N elements which N is number of variable_decl we have
        seen until now"""
    stack_local_params = []
    """this stack save number of variable_decl we have seen until now. protocol of this stack is in the following order:
    - last element ++1 when entering a new stmt_block for each variable_decl
    - last element --N when exiting a stmt_block which N is the number of variable_decl in that stmt_block
    - before every function call which is equivalent to 'jal f_label', we append 0 to stack
    - before every return which is equivalent to 'jr $ra', we pop last element of stack   
    """
    stack_local_params_count = [0]

    def __init__(self):
        super().__init__()
        self.expr_types = []
        self.stmt_labels = []
        self.loop_labels = []
        self.last_type = None

    def start(self, tree):
        return ''.join(self.visit_children(tree))

    def decl(self, tree):
        code = ''
        for decl in tree.children:
            if decl.data == 'variable_decl' or decl.data == 'function_decl':
                code += self.visit(decl)
            elif decl.data == 'class_decl':
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
                '\tlb $t0, 0($a0)\n'
                '\tlb $t1, 0($a1)\n'
                '\tbne $t0, $t1, __NE__\n'
                '\tbne $t0, $zero, __cont__\n'
                '\tli $v0, 1\n'
                '\tjr $ra\n'
                '__cont__:\n'
                '\taddi $a0, $a0, 1\n'
                '\taddi $a1, $a1, 1\n'
                '\tj __strcmp__\n'
                '__NE__:\n'
                '\tli $v0, 0\n'
                '\tjr $ra\n\n'
                '.data\n'
                '\ttrue: .asciiz "true"\n'
                '\tfalse: .asciiz "false"\n'
                '\tconst10000: .double 10000.0\n'
                '\tnw: .asciiz "\\n"\n'
            )
            code += ('.text\n'
                     'main:\n'
                     '\tla\t$ra,__end__\n')
        else:
            code += '.text\n{}:\n'.format(ident)

        self.current_scope += "/" + ident.value
        code += self.visit(formals)
        self.current_scope += "/_local"
        self.stack_local_params_count.append(0)
        code += self.visit(stmt_block)
        local_var_count = self.stack_local_params_count[-1]
        self.stack_local_params = self.stack_local_params[:-local_var_count]
        self.stack_local_params_count.pop()
        self.current_scope = pop_scope(self.current_scope)  # pop _local
        self.current_scope = pop_scope(self.current_scope)  # pop formals

        if ident == 'main':
            code += '.text\n'
            code += '__end__:\n'
            code += '\tli $v0, 10\t\t\t#exit\n'
            code += '\tsyscall\n'
        return code

    def formals(self, tree):
        code = ''
        for variable in tree.children:
            formal_name = variable.children[1].value
            formal_type = symbol_table_objects[symbol_table[(self.current_scope, formal_name)]].type
            code += '.data\n'
            code += '.align 2\n'
            if formal_type.name == 'double' and formal_type.dimension == 0:
                code += '{}: .space 8\n'.format((self.current_scope + "/" + formal_name).replace("/", "_"))
            else:
                code += '{}: .space 4\n'.format((self.current_scope + "/" + formal_name).replace("/", "_"))
        return code

    def stmt_block(self, tree):
        self.current_scope += "/" + str(self.block_stmt_counter)
        self.block_stmt_counter += 1
        code = ''
        stmt_id = cnt()
        store_len = len(self.stmt_labels)
        code += '.text\nstart_stmt_{}:\n'.format(stmt_id)
        for child in tree.children:
            if child.data == 'variable_decl':
                code += self.visit(child)
                self.stack_local_params_count[-1] += 1
                variable_name = child.children[0].children[1].value
                variable_type = symbol_table_objects[
                    symbol_table[(self.current_scope, variable_name)]].type  # TODO is current_scope set?
                self.stack_local_params.append(
                    [self.current_scope + "/" + variable_name, variable_type])  # todo must review
                code += '.text\n'
                if variable_type.name == 'double' and variable_type.dimension == 0:
                    code += '\tl.d  $f0, {}\n'.format((self.current_scope + "/" + variable_name).replace("/", "_"))
                    code += '\taddi $sp, $sp, -8\n'
                    code += '\ts.d  $f0, 0($sp)\n\n'
                else:
                    code += '\tla   $t0, {}\n'.format((self.current_scope + "/" + variable_name).replace("/", "_"))
                    code += '\tlw   $t1, 0($t0)\n'
                    code += '\taddi $sp, $sp, -8\n'
                    code += '\tsw   $t1, 0($sp)\n\n'
            else:
                code += self.visit(child)
        # pop declared variables in this scope
        for child in reversed(tree.children):
            if child.data == 'variable_decl':
                self.stack_local_params_count[-1] -= 1
                variable_name = child.children[0].children[1].value
                variable_type = symbol_table_objects[symbol_table[(self.current_scope, variable_name)]].type
                self.stack_local_params.pop()  # todo must review
                code += '.text\n'
                if variable_type.name == 'double' and variable_type.dimension == 0:
                    code += '\tl.d  $f0, 0($sp)\n'
                    code += '\taddi $sp, $sp, 8\n'
                    code += '\ts.d  $f0, {}\n\n'.format((self.current_scope + "/" + variable_name).replace("/", "_"))
                else:
                    code += '\tlw   $t1, 0($sp)\n'
                    code += '\taddi $sp, $sp, 8\n'
                    code += '\tla   $t0, {}\n'.format((self.current_scope + "/" + variable_name).replace("/", "_"))
                    code += '\tsw   $t1, 0($t0)\n\n'

        code += 'end_stmt_{}:\n'.format(stmt_id)
        self.stmt_labels = self.stmt_labels[:store_len]
        self.stmt_labels.append(stmt_id)
        self.current_scope = pop_scope(self.current_scope)
        return code
        # todo must review by Sir Sadegh

    def stmt(self, tree):
        child = tree.children[0]
        store_len = len(self.stmt_labels)
        code = ''
        if child.data == 'for_stmt':
            if child.children[0].data == 'ass':
                code += self.visit(child.children[0])

        stmt_id = cnt()
        code += ('start_stmt_{}:\n'.format(stmt_id))
        child._meta = stmt_id
        if child.data == 'if_stmt':
            code += self.visit(child)
        elif child.data == 'while_stmt':
            code += self.visit(child)
        elif child.data == 'for_stmt':
            code += self.visit(child)
        elif child.data == 'stmt_block':
            code += self.visit(child)
        elif child.data == 'break_stmt':  # there is a problem with it !
            code += self.visit(child)
        elif child.data == 'return_stmt':
            code += self.visit(child)
            # todo implement for class methods
            func_name = self.current_scope.split('/')[1]
            funct = function_objects[function_table[func_name]]
            if funct.return_type.name == 'double' and funct.return_type.dimension == 0:
                code += '\tl.d   $f30, 0($sp)\n'
                code += '\taddi $sp, $sp, 8\n'
            elif funct.return_type.name != 'void':
                code += '\tlw   $t8, 0($sp)\n'
                code += '\taddi $sp, $sp, 8\n'
            # todo wither is it essential to pop expr from stack or not or do this in caller side?
            local_var_count_of_this_scope = self.stack_local_params_count[-1]
            for local_var in reversed(self.stack_local_params[-local_var_count_of_this_scope:]):
                local_var_name = local_var[0]
                local_var_type = local_var[1]
                code += '.text\n'
                if local_var_type.name == 'double' and local_var_type.dimension == 0:
                    code += '\tl.d  $f0, 0($sp)\n'
                    code += '\taddi $sp, $sp, 8\n'
                    code += '\ts.d  $f0, {}\n\n'.format(local_var_name.replace("/", "_"))
                else:
                    code += '\tlw   $t0, 0($sp)\n'
                    code += '\taddi $sp, $sp, 8\n'
                    code += '\tsw   $t0, {}\n\n'.format(local_var_name.replace("/", "_"))
            # self.stack_local_params = self.stack_local_params[:-local_var_count_of_this_scope]
            # self.stack_local_params_count.pop()       # sepehr
            if funct.return_type.name == 'double' and funct.return_type.dimension == 0:
                code += '\taddi $sp, $sp, -8\n'
                code += '\ts.d   $f30, 0($sp)\n'
            elif funct.return_type.name != 'void':
                code += '\taddi $sp, $sp, -8\n'
                code += '\tsw   $t8, 0($sp)\n'
            code += '\tjr   $ra\n\n'
        elif child.data == 'print_stmt':
            code += self.visit(child)
        elif child.data == 'expr' or child.data == 'ass':
            code += self.visit(child)
            code += '# HERE!\n'
            # print('     ->>', child)
            expr_type = self.expr_types[-1]
            if expr_type.name != 'void':
                code += '.text\n'
                code += '\taddi\t$sp, $sp, 8\n\n'
            self.expr_types.pop()
        else:
            code += self.visit(child)
        # todo these last 4 if statements can be removed but there are here to have more explicit behavior

        code += 'end_stmt_{}:\n'.format(stmt_id)
        self.stmt_labels = self.stmt_labels[:store_len]
        self.stmt_labels.append(stmt_id)
        return code

    def break_stmt(self, tree):
        code = tab("""
            .text\t\t\t\t# break
                j end_stmt_{}
            ##             
        """.format(self.loop_labels[-1]))
        return code

    def return_stmt(self, tree):
        return ''.join(self.visit_children(tree))

    def if_stmt(self, tree):
        code = '# if starts here:\n'
        code += self.visit(tree.children[0])
        then_code = self.visit(tree.children[1])
        else_code = '' if len(tree.children) == 2 else self.visit(tree.children[2])
        if len(tree.children) == 2:
            code += tab(
                """
                .text\t\t\t\t#If
                    lw $a0, 0($sp)
                    addi $sp, $sp, 8
                    beq $a0, 0, end_stmt_{then}
                    j  start_stmt_{then}
                """.format(then=self.stmt_labels[-1])
            )
            code += then_code
        else:
            code += tab("""
                .text\t\t\t\t# IfElse
                    lw $a0, 0($sp)
                    addi $sp, $sp, 8
                    beq $a0, 0, start_stmt_{els}
                """.format(els=self.stmt_labels[-1]))
            code += then_code
            code += tab("j end_stmt_{els}".format(els=self.stmt_labels[-1]))
            code += else_code
        return code

    def while_stmt(self, tree):
        while_id = tree._meta
        self.loop_labels.append(while_id)
        store_len = len(self.stmt_labels)
        code = '.text\t\t\t\t# While\n'
        code += self.visit(tree.children[0])
        stmt_code = self.visit(tree.children[1])
        code += tab("""
            lw $a0, 0($sp)
            addi $sp, $sp, 8
            beq $a0, 0, end_stmt_{while_end}
        """.format(while_end=while_id))
        code += stmt_code
        code += tab("j start_stmt_{while_start}".format(while_start=while_id))
        self.stmt_labels = self.stmt_labels[:store_len]
        self.loop_labels.pop()
        return code

    def for_stmt(self, tree):
        code = '.text\t\t\t\t# For'
        for_id = tree._meta
        self.loop_labels.append(for_id)
        childs = tree.children
        next = ''
        if childs[0].data == 'ass':
            code += self.visit(childs[1])
        else:
            code += self.visit(childs[0])
        if childs[-2].data == 'ass':
            next += self.visit(childs[-2])
        code += tab("""
            lw $a0, 0($sp)
            addi $sp, $sp, 8
            beq $a0, $zero, end_stmt_{}
        """.format(for_id))
        code += self.visit(childs[-1])
        code += next
        code += "\tj start_stmt_{}\n".format(for_id)
        self.loop_labels.pop()
        return code

    # probably we wont need this part in cgen
    def class_decl(self, tree):
        code = ''
        ident = tree.children[0]

        if type(tree.children[1]) == lark.lexer.Token:
            pass  # it is for inheritance we scape it for now
        else:
            self.current_scope += "/__class__" + ident.value
            for field in tree.children[1:]:
                code += self.visit(field)
            self.current_scope = pop_scope(self.current_scope)
        return code

    def field(self, tree):
        code = ''
        for child in tree.children:
            if child.data == 'variable_decl':
                code += self.visit(child)
                pass
            if child.data == 'function_decl':
                code += self.visit(child)
                pass
        return code

    def variable_decl(self, tree):
        code = ''
        if '/__class__' in self.current_scope:
            return code
        variable = tree.children[0]
        var_type = variable.children[0]
        size = 4
        if type(var_type.children[0]) == lark.lexer.Token:
            var_type = var_type.children[0].value
            if var_type == 'double':
                size = 8
            elif var_type == 'string':
                code += '.data\n'
                code += '.align 2\n'
                code += self.current_scope.replace('/', '_') + '_' + variable.children[1] + ': .space ' + str(
                    size) + '\n'
                code += '.text\n'
                code += '\tli $a0, 256\n'
                code += '\tli $v0, 9\n'
                code += '\tsyscall\n'
                code += '\tsw $v0, ' + self.current_scope.replace('/', '_') + '_' + variable.children[1] + '\n\n'
                return code
        name = variable.children[1]
        code += '.data\n'
        code += '.align 2\n'
        code += self.current_scope.replace('/', '_') + '_' + name + ': .space ' + str(size) + '\n\n'
        return code

    def type(self, tree):
        if type(tree.children[0]) == lark.lexer.Token:
            self.last_type = Type(tree.children[0])
        else:
            self.visit(tree.children[0])
            self.last_type.dimension += 1
        return ''

    def expr(self, tree):
        return ''.join(self.visit_children(tree))

    def expr8(self, tree):
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
        code = tab("""
        .text\t\t\t\t # Read Line
            li $a0, 256         #Maximum string length
            li $v0, 9           #sbrk
            syscall
            sub $sp, $sp, 8
            sw $v0, 0($sp)
            move $a0, $v0
            li $a1, 256         #Maximum string length (incl. null)
            li $v0, 8           #read_string
            syscall             #ReadLine()
            
            lw $a0, 0($sp)      #Replace \\n to \\r(?)
            lw $t1, nw
            read_{label_id}:
                lb $t0, 0($a0)
                beq $t0, 10, e_read_{label_id}
                addi $a0, $a0, 1
                j read_{label_id}
            e_read_{label_id}:
                lb $t2, 1($a0)
                sb $t2, 0($a0)
        ##
        """.format(label_id=cnt()))
        self.expr_types.append(Type(Types.STRING))
        return code

    def read_integer(self, tree):
        code = tab("""
            .text\t\t\t\t # Read Integer
                li $v0, 5           #read_integer
                syscall             #ReadInteger()
                sub $sp, $sp, 8
                sw $v0, 0($sp)
            ##
            """)
        self.expr_types.append(Type(Types.INT))
        return code

    def new_array(self, tree):
        code = ''
        code += ''.join(self.visit_children(tree))
        shamt = 2
        tp = tree.children[1].children[0]
        if type(tp) == lark.lexer.Token:
            if tp.value == Types.DOUBLE:
                shamt = 3

        code += tab("""
            .text\t\t\t\t # New array
                lw $a0, 0($sp)
                addi $sp, $sp, 8
                sll $a0, $a0, {shamt}
                li $v0, 9           #sbrk
                syscall
                sub $sp, $sp, 8
                sw $v0, 0($sp)\n
            ##
        """.format(shamt=shamt))
        self.expr_types.append(Type(name=self.last_type.name, dimension=self.last_type.dimension + 1))
        return code

    def get_type(self, typ):
        if type(typ) == lark.lexer.Token:
            return Type(typ)
        ret = self.get_type(typ.children[0])
        ret.dimension += 1
        return ret

    def not_expr(self, tree):
        code = ''.join(self.visit_children(tree))
        code += tab("""
            .text\t\t\t\t # Not
                lw $t0, 0($sp)
                addi $sp, $sp, 8
                li $t1, 1
                beq $t0, 0, not_{0}
                    li $t1, 0
                not_{0}:
                    sub  $sp, $sp, 8
                    sw $t1, 0($sp)
            ##
        """.format(cnt()))
        self.expr_types.pop()
        self.expr_types.append(Type(Types.BOOL))
        return code

    def neg(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types[-1]
        if typ.name == 'int':
            code += tab("""
                .text\t\t\t\t# Neg int
                    lw $t0, 0($sp)
                    sub $t0, $zero, $t0
                    sw $t0, 0($sp)
                ##
                """)
        else:
            code += tab("""
                .text\t\t\t\t# Neg double
                    l.d $f0, 0($sp)
                    neg.d $f0, $f0
                    s.d $f0, 0($sp)
                ##
            """)
        return code

    def print(self, tree):
        code = ''
        for child in tree.children[0].children:
            code += self.visit(child)
            t = self.expr_types[-1]
            code += '.text\n'
            if t.name == 'double':
                code += tab("""
                    # Print double
                        l.d $f12, 0($sp)
                        addi $sp, $sp, 8
                        li.d $f2, 1000.0
                        mul.d $f12, $f12, $f2
                        round.w.d $f12, $f12
                        cvt.d.w $f12, $f12
                        div.d $f12, $f12, $f2
                        li $v0, 3
                        syscall             #Print double
                    ##
                """)
            #                 print("""
            # l.d $f12, 0($sp)
            # addi $sp, $sp, 8
            # li $v0, 3
            # syscall
            #                 """)
            elif t.name == 'int':
                code += tab("""
                    # Print int
                        li $v0, 1
                        lw $a0, 0($sp)
                        addi $sp, $sp, 8
                        syscall             #Print int
                    ##
                """)
            elif t.name == Types.STRING:
                code += tab(
                    """
                    # Print string
                        li $v0, 4
                        lw $a0, 0($sp)
                        addi $sp, $sp, 8
                        syscall             #Print string
                    ##
                    """)
            elif t.name == 'bool' and t.dimension == 0:
                code += tab(
                    """
                    # Print bool
                        lw $a0, 0($sp)
                        addi $sp, $sp, 8
                        beq $a0, 0, zero_{cnt}
                        li $v0, 4
                        la $a0, true
                        syscall
                        j ezero_{cnt}
                        zero_{cnt}:
                        li $v0, 4
                        la $a0, false
                        syscall             #Print bool
                        ezero_{cnt}:
                    ##
                    """.format(cnt=cnt())
                )
        # '\n' at the end of print
        code += tab(
            """
            # Print new line
                li $v0, 4
                la $a0, nw
                syscall\t\t\t\t#Print new line\n
            ##
            """)
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
        # self.expr_types
        if len(tree.children) == 3:
            # it's for class
            # todo must be done
            pass
        if len(tree.children) == 2:
            # self.stack_local_params_count.append(0)
            ident = tree.children[0]
            actuals = tree.children[1]
            name = ident.value
            actuals._meta = name
            return self.visit(actuals)

    def actuals(self, tree):
        code = '.text\n'
        function_name = tree._meta
        function_scope = 'root/' + function_name
        actual_counter = 0
        function = function_objects[function_table[function_name]]
        # push formal parameter
        for formal in function.formals:

            formal_name = (function_scope + "/" + formal[0]).replace("/", "_")
            formal_type = formal[1]
            if formal_type.name == 'double' and formal_type.dimension == 0:
                code += '\tl.d  $f0, {}\n'.format(formal_name)
                code += '\taddi $sp, $sp, -8\n'
                code += '\ts.d  $f0, 0($sp)\n\n'
            else:
                code += '\tlw   $t1, {}\n'.format(formal_name)
                code += '\taddi $sp, $sp, -8\n'
                code += '\tsw   $t1, 0($sp)\n\n'

        # set actual parameters to formal parameters
        for expr in tree.children:
            code += self.visit(expr)
            formal_name = function.formals[actual_counter][0]
            code += '.text\n'
            formal_type = function.formals[actual_counter][1].name
            if formal_type == 'double':
                code += '\tl.d  $f0, 0($sp)\n'
                code += '\ts.d  $f0, {}\n'.format((function_scope + "/" + formal_name).replace("/", "_"))
                code += '\taddi $sp, $sp, 8\n\n'
            else:
                code += '\tlw   $v0, 0($sp)\n'
                code += '\tsw   $v0, {}\n'.format((function_scope + "/" + formal_name).replace("/", "_"))
                code += '\taddi $sp, $sp, 8\n\n'
            actual_counter += 1

        code += '.text\n'
        code += '\taddi $sp, $sp, -8\n'
        code += '\tsw   $ra, 0($sp)\n'
        code += '\tjal {}\n'.format(function_name)
        if function.return_type.name == 'double' and function.return_type.dimension == 0:
            code += '\tl.d   $f30, 0($sp)\n'
            code += '\taddi $sp, $sp, 8\n'
        elif function.return_type.name != 'void':
            code += '\tlw   $t8, 0($sp)\n'
            code += '\taddi $sp, $sp, 8\n'
        code += '\tlw   $ra, 0($sp)\n'
        code += '\taddi $sp, $sp, 8\n\n'
        # pop formal parameters
        for formal in reversed(function.formals):
            formal_name = (function_scope + "/" + formal[0]).replace("/", "_")
            formal_type = formal[1]
            if formal_type.name == 'double':
                code += '\tl.d  $f0, 0($sp)\n'
                code += '\taddi $sp, $sp, 8\n'
                code += '\ts.d  $f0, {}\n\n'.format(formal_name)
            else:
                code += '\tlw   $t0, 0($sp)\n'
                code += '\taddi $sp, $sp, 8\n'
                code += '\tsw   $t0, {}\n\n'.format(formal_name)
        if function.return_type.name == 'double' and function.return_type.dimension == 0:
            code += '\taddi $sp, $sp, -8\n'
            code += '\ts.d   $f30, 0($sp)\n'
        elif function.return_type.name != 'void':
            code += '\taddi $sp, $sp, -8\n'
            code += '\tsw   $t8, 0($sp)\n'
        code += '# return type is ' + function.return_type.name + ' ' + str(function.return_type.dimension)
        code += '\n'
        self.expr_types.append(deepcopy(function.return_type))
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
            code += '\tlw   $t0, 0($sp)\n'
            code += '\tlw   $t1, 8($sp)\n'
            code += '\tmul  $t2, $t1, $t0\n'
            code += '\tsw   $t2, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        if typ.name == 'double':
            code += '.text\n'
            code += '\tl.d      $f0, 0($sp)\n'
            code += '\tl.d      $f2, 8($sp)\n'
            code += '\tmul.d    $f4, $f2, $f0\n'
            code += '\ts.d      $f4, 8($sp)\n'
            code += '\taddi     $sp, $sp, 8\n\n'
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
            code += '\tlw $a0, 0($a0)\n'
            code += '\tlw $a1, 8($sp)\n'
            code += '\tlw $a1, 0($a1)\n'
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
        self.expr_types.append(Type(Types.BOOL))
        return code

    def null(self, tree):
        code = '.text\n'
        code += '\tsub $sp, $sp, 4\n'
        code += '\tsw $zero, 0($sp)\n\n'
        self.expr_types.append(Type('null'))
        return code

    def l_value(self, tree):
        return ''.join(self.visit_children(tree))

    def var_addr(self, tree):
        var_scope = self.current_scope
        var_name = tree.children[0].value
        while (var_scope, var_name) not in symbol_table:
            var_scope = pop_scope(var_scope)
            # inja :D chon ta'rif nashode, while tamum nemishe; dombale moteghayyere dorost migardam dg. be scope asli kar nadaram. mannnnnnn kari lazem nist bokonim. code ghalat nemidan ke. Re Dg:)) tarif nakardam y ro
        label_name = var_scope.replace('/', '_') + '_' + var_name
        code = '.text\n'
        code += '\tla $t0, {}\n'.format(label_name)
        code += '\tsub $sp, $sp, 8\n'
        code += '\tsw $t0, 0($sp)\n\n'
        typ = symbol_table_objects[symbol_table[var_scope, var_name]].type
        new_type = Type(name=typ.name, meta=typ._meta)
        new_type.dimension = typ.dimension
        self.expr_types.append(new_type)
        return code

    def subscript(self, tree):
        code = ''.join(self.visit_children(tree))
        self.expr_types.pop()
        typ = self.expr_types[-1]
        if typ.name == Types.DOUBLE and typ.dimension == 1:
            code += '.text\n'
            code += '\tlw $t7, 8($sp)\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tli $t1, 8\n'
            code += '\tmul $t0, $t0, $t1\n'
            code += '\tadd $t1, $t0, $t7\n'
            code += '\tsw $t1, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        else:
            code += '.text\n'
            code += '\tlw $t7, 8($sp)\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tli $t1, 4\n'
            code += '\tmul $t0, $t0, $t1\n'
            code += '\tadd $t1, $t0, $t7\n'
            code += '\tsw $t1, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types[-1].dimension -= 1
        return code

    def val(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types[-1]
        if typ.name == 'double' and typ.dimension == 0:
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tl.d $f0, 0($t0)\n'
            code += '\ts.d $f0, 0($sp)\n\n'
        else:
            code += '.text\n'
            code += '\tlw $t0, 0($sp)\n'
            code += '\tlw $t0, 0($t0)\n'
            code += '\tsw $t0, 0($sp)\n\n'
        return code

    def ass(self, tree):
        code = ''.join(self.visit_children(tree))
        typ = self.expr_types[-1]
        if typ.name == 'double' and typ.dimension == 0:
            code += '.text\n'
            code += '\tlw $t0, 8($sp)\n'
            code += '\tl.d $f0, 0($sp)\n'
            code += '\ts.d $f0, 0($t0)\n'
            code += '\ts.d $f0, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        else:
            code += '.text\n'
            code += '\tlw $t0, 8($sp)\n'
            code += '\tlw $t1, 0($sp)\n'
            code += '\tsw $t1, 0($t0)\n'
            code += '\tsw $t1, 8($sp)\n'
            code += '\taddi $sp, $sp, 8\n\n'
        self.expr_types.pop()
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
class Person{
    int mmd(){}
}
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


def cgen(decaf):
    parser = Lark(grammar, parser="lalr")
    parse_tree = parser.parse(decaf)
    SymbolTableMaker().visit(parse_tree)
    return CodeGenerator().visit(parse_tree)


decaf = """


void f(int x, int y, bool z, double a){
    if(x == 1 && y == 2 && z == true && a > 2.5){
        Print("ok");
        x = 10;
        y = 100;
        z = false;
        a = 1.5123;
        return;
    }
    Print("not ok");
    return;
}

int main()  {
    int x;
    bool y;
    double aa; 
    x = 1;
    y = true;
    aa = 10.2;
    f(x, 2, y, 10.2);
    Print(x);
    if(y){
        Print("true");
    }
    Print(aa);
    return;
}
"""

decaf = r"""
double f(double x) {
    return x + 1.0;
}

int power(int i) {
    int x;
    x = -5;
    x = i - 8;
    if (i > 0)
        power(i - 1);
    else {
        Print(f(3.14));
        return 8;
    }
    Print("1: ", i, ", 2: ", x);
    i = 800 + i;
    return i * 2;
}

int main() {
    power(5);
    return 68;
}
"""

if __name__ == '__main__':
    # print(cgen("""
#
# int jumper_3(int x){
#     Print("3 ", x);
#     x = 1;
#     Print("3 ", x);
#     return 0;
# }
#
# int jumper_2(int y){
#     Print("2 ", y);
#     jumper_3(y);
#     Print("2 ", y);
#     jumper_3(y+1);
#     Print("2 ", y);
#     return 0;
# }
#
# int jumper_1(int x){
#     Print("1 ", x);
#     jumper_2(x);
#     Print("1 ", x);
#     jumper_2(x);
#     Print("1 ", x);
#     return 0;
# }
#
# int f(){
#     jumper_1(10);
#     return 0;
# }
#
# int main()  {
#     f();
#     return 0;
# }
#
#
#
#     """))
    print(cgen(decaf))
    exit(0)
    # (cgen("""
    #     int main(){
    #
    #         NewArray(5, double[][]);
    #         NewArray(5, int);
    #         NewArray(5, bool[]);
    #         for(i=0; i<10; i=i+1){
    #         }
    #     }
    # """))
    # exit(0)
    # print(cgen("""
    # int main(){
    #     while(true){
    #         if(ReadInteger() == 2){
    #             Print(2);
    #             break;
    #         }
    #         Print(1);
    #     }
    #     while(true){
    #         while(true){
    #             if(ReadInteger() == 2){
    #                 Print(4);
    #                 break;
    #             }
    #             Print(3);
    #         }
    #         while(true){
    #             if (false){
    #             }else{
    #                 break;
    #             }
    #             Print("holy");
    #         }
    #         break;
    #     }
    #     Print("goody goody");
    # }
    # """))
    #
    #     exit(0)

    parser = Lark(grammar, parser="lalr")
    parse_tree = parser.parse(text=decaf)
    SymbolTableMaker().visit(parse_tree)
    ClassTreeSetter().visit(parse_tree)
    set_inheritance()
    print(CodeGenerator().visit(parse_tree))
    print(parse_tree.pret)
    pass

"""
power(i){
    int x ;
    x = -5;
    x = i;
    if (i > 0) {
        int i;
        power(i-1)
    }
    if i == 0:
        :return
    print(x)
    :return
}

power(3) //jal

power/i = 2
power/local/x = 2
power/local/1/i

stack_mips[?,ra,?|,3,ra,3]
stack_local_params =[x,x,x,i] //when enter a statement push per each declaration
                                //
stack_local_params_cnt =[1,1,2,0] //when new call push 
                                //when new statement +1
console:
1
2
"""
