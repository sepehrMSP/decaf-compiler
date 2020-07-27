from lark import Lark
from lark.visitors import Interpreter, Transformer


class TestInterpreter(Interpreter):
    def start(self, tree):
        print("oomadim too")
        # print(tree.data)
        # print(tree.children)
        self.visit_children(tree)
        # self.visit_children(tree.children)
        # self.visit(tree.children[0][1])

    def section(self, tree):
        print("lamassab")
        self.visit_children(tree)


    def kk1(self, tree):
        print(tree.children)
        res = self.visit_children(tree)
        print(res)



if __name__ == '__main__':
    parser2 = Lark(r"""
            start: _NL? section+
            section: "[" NAME "]" _NL item+
            item: NAME "=" VALUE? _NL -> kk1 
                | NAME "****"
            VALUE: /./+
            %import common.CNAME -> NAME
            %import common.NEWLINE -> _NL
            %import common.WS_INLINE
            %ignore WS_INLINE
        """, parser="lalr")
    sample_conf = """
    [bla]
    a=Hello
    this="that",4
    empty=
    """

    tri2 = parser2.parse(sample_conf)

    TestInterpreter().visit(tri2)