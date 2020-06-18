from lark import Lark

g = ''' start: IDENT | BOOL
        IDENT :  /(?!((true)|(false)|(void)|(int)|(double)|(bool)|(string)|(class)|(interface)|(null)|(this)|(extends)|(implements)|(for)|(while)|(if)|(else)|(return)|(break)|(new)|(NewArray)|(Print)|(ReadInteger)|(ReadLine))([^_a-zA-Z0-9]|$))[a-zA-Z][_a-zA-Z0-9]*/
        BOOL : /((true)|(false))(xabc1235ll)*/
'''

print(Lark(grammar=g, parser='lalr').parse(input()))