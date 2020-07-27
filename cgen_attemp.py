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


class CodeGenerator(Interpreter):
    current_scope = 'root'
    block_stmt_counter = 0

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

        self.current_scope += "/" + ident.value
        self.visit(formals)
        self.current_scope += "/_local"
        self.current_scope += "/" + str(self.block_stmt_counter)
        self.block_stmt_counter += 1
        self.visit_children(tree)
        pop_scope(self.current_scope)  # pop stmt block
        pop_scope(self.current_scope)  # pop _local
        pop_scope(self.current_scope)  # pop formals

    def formals(self, tree):
        self.visit_children(tree)

    #     pass

    def stmt_block(self, tree):
        self.visit_children(tree)

    def stmt(self, tree):
        child = tree.children[0]
        if child.data == 'if_stmt':
            self.visit(child)
        if child.data == 'while_stmt':
            self.visit(child)
        if child.data == 'for_stsmt':
            self.visit(child)
        if child.data == 'stmt_block':
            self.current_scope += "/" + str(self.block_stmt_counter)
            self.block_stmt_counter += 1
            self.visit(child)
            pop_scope(self.current_scope)
        if child.data == 'break_stmt':  # there is a problem with it !
            pass
            # call a function just for break wellformness!it should move back on the stack maybe not in this interpreter
        if child.data == 'return_stmt':
            pass
        if child.data == 'print_stmt':
            pass
        if child.data == 'expr':
            self.visit(child)
            pass
        # todo these last 4 if statements can be removed but there are here to have more explicit behavior

    def if_stmt(self, tree):
        self.visit_children(tree)

    #     pass

    def while_stmt(self, tree):
        self.visit_children(tree)

    #     pass

    def for_stmt(self, tree):
        self.visit_children(tree)
        pass

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

        pass

    def variable_decl(self, tree):
        if '/__class__' in self.current_scope:
            return
        variable = tree.children[0]
        var_type = variable.children[0]
        if type(var_type.children[0]) == lark.lexer.Token:
            var_type = var_type.children[0].value
            if var_type not in ['int', 'double', 'bool']:
                return
        size = 4
        if var_type == 'double':
            size = 8
        name = variable.children[1]
        print('.data')
        print(self.current_scope.replace('/', '_') + '_' + name + ': .space ' + str(size))

    def variable(self, tree):
        self.visit_children(tree)

    #     pass

    def type(self, tree):
        self.visit_children(tree)

    def expr(self, tree):
        self.visit_children(tree)

        # print('heyyy')

    def expr(self, tree):
        self.visit_children(tree)

    def read_line(self, tree):
        """
        line address in stack
        """
        print("""
            .data
                str: .space 256
            .text
                li $v0, 8
                la $a0, str
                li $a1, 256
                syscall
                sub $sp, $sp, 4
                sw $a0, 0($sp)
        """)

    def read_integer(self, tree):
        print("""
            li $v0, 5 #get a from input
            syscall
            sub $sp, $sp, 4
            sw $v0, 0($sp)
        """)

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

    name = ReadLine();
    age = ReadInteger();

    p = new Person;
    p.setName(name);
    p.setAge(age);

    p.print();
}
"""

if __name__ == '__main__':
    parser = Lark(grammar, parser="lalr")
    parse_tree = parser.parse(decaf)
    SymbolTableMaker().visit(parse_tree)
    CodeGenerator().visit(parse_tree)
    pass
