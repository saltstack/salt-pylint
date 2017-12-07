# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`


    ==========================================
    PyLint Extended String Formatting Checkers
    ==========================================

    Proper string formatting PyLint checker
'''

# Import Python libs
from __future__ import absolute_import
import re
import sys

# Import PyLint libs
try:
    # >= pylint 1.0
    import astroid
except ImportError:  # pylint < 1.0
    from logilab import astng as astroid  # pylint: disable=no-name-in-module
from pylint.checkers import utils
from pylint.checkers import BaseChecker
from pylint.checkers.utils import check_messages, parse_format_string

try:
    # >= pylint 1.0
    from pylint.interfaces import IAstroidChecker
except ImportError:  # < pylint 1.0
    from pylint.interfaces import IASTNGChecker as IAstroidChecker  # pylint: disable=no-name-in-module

# Import 3rd-party libs
import six


MSGS = {
    'W1320': ('String format call with un-indexed curly braces: %r',
              'un-indexed-curly-braces-warning',
              'Under python 2.6 the curly braces on a \'string.format()\' '
              'call MUST be indexed.'),
    'E1320': ('String format call with un-indexed curly braces: %r',
              'un-indexed-curly-braces-error',
              'Under python 2.6 the curly braces on a \'string.format()\' '
              'call MUST be indexed.'),
    'W1321': ('String substitution used instead of string formattting on: %r',
              'string-substitution-usage-warning',
              'String substitution used instead of string formattting'),
    'E1321': ('String substitution used instead of string formattting on: %r',
              'string-substitution-usage-error',
              'String substitution used instead of string formattting'),
    'E1322': ('Repr flag (!r) used in string: %r',
              'repr-flag-used-in-string',
              'Repr flag (!r) used in string'),
    'E1323': ('Non-unicode-string: %r',
              'non-unicode-string',
              'Non-unicode string'),
    'E1324': ('String formatting used in logging: %r',
              'str-format-in-logging',
              'String formatting used in logging'),
}

BAD_FORMATTING_SLOT = re.compile(r'(\{![\w]{1}\}|\{\})')


class StringCurlyBracesFormatIndexChecker(BaseChecker):

    __implements__ = IAstroidChecker

    name = 'string'
    msgs = MSGS
    priority = -1

    options = (('un-indexed-curly-braces-always-error',
                {'default': 1, 'type': 'yn', 'metavar': '<y_or_n>',
                 'help': 'Force un-indexed curly braces on a '
                         '\'string.format()\' call to always be an error.'}
                ),
                ('enforce-string-formatting-over-substitution',
                 {'default': 1, 'type': 'yn', 'metavar': '<y_or_n>',
                  'help': 'Enforce string formatting over string substitution'}
                 ),
                ('string-substitutions-usage-is-an-error',
                 {'default': 1, 'type': 'yn', 'metavar': '<y_or_n>',
                  'help': 'Force string substitution usage on strings '
                          'to always be an error.'}
                 ),
               )

    @check_messages(*(MSGS.keys()))
    def visit_binop(self, node):
        if not self.config.enforce_string_formatting_over_substitution:
            return

        if node.op != '%':
            return

        if not (isinstance(node.left, astroid.Const) and
                isinstance(node.left.value, six.string_types)):
            return

        try:
            required_keys, required_num_args = parse_format_string(node.left.value)
        except (utils.UnsupportedFormatCharacter, utils.IncompleteFormatString):
            # This is handled elsewere
            return

        if required_keys or required_num_args:
            if self.config.string_substitutions_usage_is_an_error:
                msgid = 'E1321'
            else:
                msgid = 'W1321'
            self.add_message(
                msgid, node=node.left, args=node.left.value
            )

        if '!r}' in node.left.value:
            self.add_message(
                'E1322', node=node.left, args=node.left.value
            )

    @check_messages(*(MSGS.keys()))
    def visit_callfunc(self, node):
        self.visit_call(node)

    @check_messages(*(MSGS.keys()))
    def visit_call(self, node):
        func = utils.safe_infer(node.func)
        if isinstance(func, astroid.BoundMethod) and func.name == 'format':
            # If there's a .format() call, run the code below

            if isinstance(node.func.expr, (astroid.Name, astroid.Const)):
                # This is for:
                #   foo = 'Foo {} bar'
                #   print(foo.format(blah)
                for inferred in node.func.expr.infer():
                    if not hasattr(inferred, 'value'):
                        # If there's no value attribute, it's not worth
                        # checking.
                        continue

                    if not isinstance(inferred.value, six.string_types):
                        # If it's not a string, continue
                        continue

                    if '!r}' in inferred.value:
                        self.add_message(
                            'E1322', node=inferred, args=inferred.value
                        )

                    if BAD_FORMATTING_SLOT.findall(inferred.value):
                        if self.config.un_indexed_curly_braces_always_error or \
                                sys.version_info[:2] < (2, 7):
                            msgid = 'E1320'
                        else:
                            msgid = 'W1320'
                        self.add_message(
                            msgid, node=inferred, args=inferred.value
                        )
                try:
                    # Walk back up until no parents are found and look for a
                    # logging.RootLogger instance in the parent types
                    ptr = node
                    while True:
                        parent = ptr.parent
                        for inferred in parent.func.expr.infer():
                            try:
                                instance_type = inferred.pytype().split('.')[0]
                            except TypeError:
                                continue
                            if instance_type == 'logging':
                                self.add_message(
                                    'E1324',
                                    node=node,
                                    args=node.as_string(),
                                )
                        ptr = parent
                except (AttributeError, astroid.exceptions.NameInferenceError):
                    pass

            elif not hasattr(node.func.expr, 'value'):
                # If it does not have an value attribute, it's not worth
                # checking
                return
            elif isinstance(node.func.expr.value, astroid.Name):
                # No need to check these either
                return
            elif BAD_FORMATTING_SLOT.findall(node.func.expr.value):
                if self.config.un_indexed_curly_braces_always_error or \
                        sys.version_info[:2] < (2, 7):
                    msgid = 'E1320'
                else:
                    msgid = 'W1320'
                self.add_message(
                    'E1320', node=node, args=node.func.expr.value
                )

    @check_messages(*(MSGS.keys()))
    def visit_const(self, node):
        '''
        Flag non-unicode string literals
        '''
        if not six.PY2 or not isinstance(node.value, six.string_types):
            return
        if isinstance(node.value, str):
            self.add_message('E1323', node=node, args=node.value)


def register(linter):
    '''required method to auto register this checker '''
    linter.register_checker(StringCurlyBracesFormatIndexChecker(linter))
