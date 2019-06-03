# -*- coding: utf-8 -*-
# Import Python libs
from __future__ import absolute_import

# Import PyLint libs
try:
    # >= pylint 1.0
    import astroid
except ImportError:  # pylint < 1.0
    from logilab import astng as astroid  # pylint: disable=no-name-in-module
from saltpylint.checkers import BaseChecker, utils

try:
    # >= pylint 1.0
    from pylint.interfaces import IAstroidChecker
except ImportError:  # < pylint 1.0
    from pylint.interfaces import IASTNGChecker as IAstroidChecker  # pylint: disable=no-name-in-module

try:
    from astroid.exceptions import NameInferenceError
except ImportError:
    class NameInferenceError(Exception):
        pass

WARNING_CODE = 'W1701'


class DunderDelChecker(BaseChecker):
    '''
    info: This class is used by pylint that checks
    if "__del__" is not used
    if "__del__" is used then a warning will be raised
    '''
    __implements__ = IAstroidChecker

    name = 'dunder-del'
    priority = -1
    msgs = {
        WARNING_CODE: (
            '"__del__" is not allowed!',
            'no-dunder-del',
            '"__del__" is not allowed! A "with" block could be a good solution'
        ),
    }

    def visit_functiondef(self, node):
        '''
        :param node: info about a function or method
        :return: None
        '''
        if node.name == "__del__":
            self.add_message(WARNING_CODE, node=node)


def register(linter):
    '''required method to auto register this checker '''
    linter.register_checker(DunderDelChecker(linter))
