from lark import Lark

grammar = """

"""


def syntax_error(code: str) -> 'str':
    """
    check compile errors

    Args:
        code (str): code to check for compile error

    Returns:
        str:
            return "NO" if there is no compile error.
            otherwise returns "YES"
    """
    try:
        Lark(grammar, parser="lalr").parse(code)
    except Exception as e:
        print(type(e))
        return "YES"

    return "NO"
