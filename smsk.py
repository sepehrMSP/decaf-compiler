from sys import stdin
from lark import Lark, Transformer

g = ''' start: t*
        t: T_ID | T_INTLITERAL | T_DOUBLELITERAL | T_STRINGLITERAL | T_BOOLEANLITERAL | RESERVED
        T_ID :  /[a-z][a-z0-9_]{,30}/i
        T_INTLITERAL : /[0-9]+/i  | /0x[a-f0-9]+/i
        T_DOUBLELITERAL: /(\\d)+\\.(\\d)*/ | /(\\d)*\\.(\\d)+/ | /(\\d)+\.(\\d)*E[+-]?(\\d)+/
        T_STRINGLITERAL : /"[^\\n"]*"/
        T_BOOLEANLITERAL.2 : "true" | "false"
        RESERVED.2 : "{" | "}" | "+" | "-" | "*" | "/" | "%" | "<" | "<=" | ">" | ">=" | "==" | "=" | "!=" | "&&" | "||"
         | "!" | ";" | "," | "." | "[]" | "[" | "]" | "(" | ")" | "void" | "interface" | "double" | "bool" | "string"
         | "class" | "int" | "null" | "this" | "extend" | "implement" | "for" | "while" | "if" | "else" | "return"
         | "break" | "new" | "NewArray" | "Print" | "ReadInteger" | "ReadLine"
        SL_COMMENT: "//" /[^\\n]*/ "\\n"
        ML_COMMENT: "/*" /(\*(?!\/)|[^*])*/ "*/"
        %ignore SL_COMMENT
        %ignore ML_COMMENT
        %import common.WS
        %ignore WS
    '''


class CodeGen(Transformer):
    def t(self, args):
        token = args[0]
        if token.type == 'RESERVED':
            print(token.value)
        else:
            print(token.type + ' ' + token.value)


l = Lark(g, transformer=CodeGen(), parser='lalr')

for line in stdin:
    l.parse(line)
