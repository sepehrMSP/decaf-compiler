import lark
from lark import Lark
from lark.visitors import Interpreter
from symbol_table_creation_attemp import symbol_table_objects, parse_tree, class_type_objects, function_objects, \
    class_table, function_table


def pop_scope(scope):
    scopes = scope.split('/')
    scopes.pop()
    parent_scope = '/'.join(scopes)
    return parent_scope


class CodeGenerator(Interpreter):
    current_scope = 'root/'
    block_stmt_counter = 0

    def decl(self, tree):
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

        self.current_scope += "/" + ident.value
        self.visit(formals)
        self.current_scope += "/_local"
        self.current_scope += "/" + str(self.block_stmt_counter)
        self.block_stmt_counter += 1
        self.visit(stmt_block)
        pop_scope(self.current_scope)  # pop stmt block
        pop_scope(self.current_scope)  # pop _local
        pop_scope(self.current_scope)  # pop formals

    def formals(self, tree):
        pass

    def stmt_block(self, tree):
        pass

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
            pass
        # todo these last 4 if statements can be removed but there are here to have more explicit behavior

    def if_stmt(self, tree):
        pass

    def while_stmt(self, tree):
        pass

    def for_stmt(self, tree):
        pass

    # probably we wont need this part in cgen
    def class_decl(self, tree):
        ident = tree.children[0]

        if type(tree.children[1]) == lark.lexer.Token:
            pass  # it is for inheritance we scape it for now
        else:
            self.current_scope += "/" + ident.value
            for field in tree.children[1:-1]:
                self.visit(field)

    def field(self, tree):
        pass

    def variable_decl(self, tree):
        pass

    def variable(self, tree):
        pass

    def type(self, tree):
        pass


if __name__ == '__main__':
    pass
