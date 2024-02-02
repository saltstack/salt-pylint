from typing import ClassVar

from pylint.checkers import BaseChecker

WARNING_CODE = "W1701"


class DunderDelChecker(BaseChecker):
    """info: This class is used by pylint that checks
    if "__del__" is not used
    if "__del__" is used then a warning will be raised.
    """

    name = "dunder-del"
    priority = -1
    msgs: ClassVar = {
        WARNING_CODE: (
            '"__del__" is not allowed!',
            "no-dunder-del",
            '"__del__" is not allowed! A "with" block could be a good solution',
        ),
    }

    def visit_functiondef(self, node):
        """:param node: info about a function or method
        :return: None
        """
        if node.name == "__del__":
            self.add_message(WARNING_CODE, node=node)


def register(linter):
    """Required method to auto register this checker."""
    linter.register_checker(DunderDelChecker(linter))
