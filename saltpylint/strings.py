"""
PyLint Extended String Formatting Checkers
==========================================

Proper string formatting PyLint checker
"""

import re
import sys
import tokenize

import astroid
from astroid.exceptions import InferenceError
from astroid.exceptions import NameInferenceError
from pylint.checkers import BaseChecker
from pylint.checkers import BaseTokenChecker
from pylint.checkers import utils

STRING_FORMAT_MSGS = {
    "W1320": (
        "String format call with un-indexed curly braces: %r",
        "un-indexed-curly-braces-warning",
        "Under python 2.6 the curly braces on a 'string.format()' call MUST be indexed.",
    ),
    "E1320": (
        "String format call with un-indexed curly braces: %r",
        "un-indexed-curly-braces-error",
        "Under python 2.6 the curly braces on a 'string.format()' call MUST be indexed.",
    ),
    "W1321": (
        "String substitution used instead of string formattting on: %r",
        "string-substitution-usage-warning",
        "String substitution used instead of string formattting",
    ),
    "E1321": (
        "String substitution used instead of string formattting on: %r",
        "string-substitution-usage-error",
        "String substitution used instead of string formattting",
    ),
    "E1322": (
        "Repr flag (!r) used in string: %r",
        "repr-flag-used-in-string",
        "Repr flag (!r) used in string",
    ),
    "E1323": (
        "String formatting used in logging: %r",
        "str-format-in-logging",
        "String formatting used in logging",
    ),
}

BAD_FORMATTING_SLOT = re.compile(r"(\{![\w]{1}\}|\{\})")


class StringCurlyBracesFormatIndexChecker(BaseChecker):
    name = "string"
    msgs = STRING_FORMAT_MSGS
    priority = -1

    options = (
        (
            "un-indexed-curly-braces-always-error",
            {
                "default": 1,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Force un-indexed curly braces on a "
                "'string.format()' call to always be an error.",
            },
        ),
        (
            "enforce-string-formatting-over-substitution",
            {
                "default": 1,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Enforce string formatting over string substitution",
            },
        ),
        (
            "string-substitutions-usage-is-an-error",
            {
                "default": 1,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Force string substitution usage on strings to always be an error.",
            },
        ),
    )

    def visit_binop(self, node):
        if node.op != "%":
            return

        if not (isinstance(node.left, astroid.Const) and isinstance(node.left.value, str)):
            return

        try:
            required_keys, required_num_args = utils.parse_format_string(node.left.value)[:2]
        except (utils.UnsupportedFormatCharacter, utils.IncompleteFormatString):
            # This is handled elsewere
            return

        if required_keys or required_num_args:
            if self.linter.config.string_substitutions_usage_is_an_error:
                msgid = "E1321"
            else:
                msgid = "W1321"
            self.add_message(msgid, node=node.left, args=node.left.value)

        if "!r}" in node.left.value:
            self.add_message("E1322", node=node.left, args=node.left.value)

    def visit_call(self, node):
        func = utils.safe_infer(node.func)
        if isinstance(func, astroid.BoundMethod) and func.name == "format":
            # If there's a .format() call, run the code below

            if isinstance(node.func.expr, (astroid.Name, astroid.Const)):
                # This is for:
                #   foo = 'Foo {} bar'
                #   print(foo.format(blah)
                for inferred in node.func.expr.infer():
                    if not hasattr(inferred, "value"):
                        # If there's no value attribute, it's not worth
                        # checking.
                        continue

                    if not isinstance(inferred.value, str):
                        # If it's not a string, continue
                        continue

                    if "!r}" in inferred.value:
                        self.add_message("E1322", node=inferred, args=inferred.value)

                    if (
                        BAD_FORMATTING_SLOT.findall(inferred.value)
                        and self.linter.config.un_indexed_curly_braces_always_error
                    ):
                        self.add_message("E1320", node=inferred, args=inferred.value)

                try:
                    # Walk back up until no parents are found and look for a
                    # logging.RootLogger instance in the parent types
                    ptr = node
                    while True:
                        parent = ptr.parent
                        for inferred in parent.func.expr.infer():
                            try:
                                instance_type = inferred.pytype().split(".")[0]
                            except TypeError:
                                continue
                            if instance_type == "logging":
                                self.add_message(
                                    "E1323",
                                    node=node,
                                    args=node.as_string(),
                                )
                                break
                        ptr = parent
                except (AttributeError, InferenceError, NameInferenceError):
                    pass

            elif not hasattr(node.func.expr, "value"):
                # If it does not have an value attribute, it's not worth
                # checking
                return
            elif isinstance(node.func.expr.value, astroid.Name):
                # No need to check these either
                return
            elif BAD_FORMATTING_SLOT.findall(node.func.expr.value):
                if self.config.un_indexed_curly_braces_always_error or sys.version_info[:2] < (
                    2,
                    7,
                ):
                    pass
                else:
                    pass
                self.add_message("E1320", node=node, args=node.func.expr.value)


STRING_LITERALS_MSGS = {
    "E1400": (
        "Null byte used in unicode string literal (should be wrapped in str())",
        "null-byte-unicode-literal",
        "Null byte used in unicode string literal",
    ),
}


class StringLiteralChecker(BaseTokenChecker):
    """Check string literals."""

    name = "string_literal"
    msgs = STRING_LITERALS_MSGS

    def process_module(self, module):
        self._unicode_literals = "unicode_literals" in module.future_imports

    def process_tokens(self, tokens):
        for tok_type, token, (start_row, _), _, _ in tokens:
            if tok_type == tokenize.STRING:
                # 'token' is the whole un-parsed token; we can look at the start
                # of it to see whether it's a raw or unicode string etc.
                self.process_string_token(token, start_row)

    def process_non_raw_string_token(self, prefix, string_body, start_row):
        """Check for bad escapes in a non-raw string.

        prefix: lowercase string of eg 'ur' string prefix markers.
        string_body: the un-parsed body of the string, not including the quote
        marks.
        start_row: integer line number in the source.
        """
        if "u" in prefix and string_body.find("\\0") != -1:
            self.add_message("null-byte-unicode-literal", line=start_row)


def register(linter):
    """Required method to auto register this checker."""
    linter.register_checker(StringCurlyBracesFormatIndexChecker(linter))
    linter.register_checker(StringLiteralChecker(linter))
