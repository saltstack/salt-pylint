from typing import ClassVar

import astroid
from pylint.checkers import BaseChecker

VIRT_LOG = "log-in-virtual"


class VirtChecker(BaseChecker):
    """checks for compliance inside __virtual__."""

    name = "virt-checker"

    msgs: ClassVar = {
        "E1401": (
            "Log statement detected inside __virtual__ function. Remove it.",
            VIRT_LOG,
            "Loader processes __virtual__ so logging not in scope",
        ),
    }
    options = ()

    priority = -1

    def visit_functiondef(self, node):
        """Verifies no logger statements inside __virtual__."""
        if (
            not isinstance(node, astroid.FunctionDef)
            or node.is_method()
            or node.type != "function"
            or not node.body
        ):
            # only process functions
            return

        try:
            if node.name != "__virtual__":
                # only need to process the __virtual__ function
                return
        except AttributeError:
            return

        # walk contents of __virtual__ function
        for child in node.get_children():
            for functions in child.get_children():
                if isinstance(functions, astroid.Call) and isinstance(
                    functions.func,
                    astroid.Attribute,
                ):
                    try:
                        # Inspect each statement for an instance of 'logging'
                        for inferred in functions.func.expr.infer():
                            try:
                                instance_type = inferred.pytype().split(".")[0]
                            except TypeError:
                                continue
                            if instance_type == "logging":
                                self.add_message(VIRT_LOG, node=functions)
                                # Found logger, don't need to keep processing this line
                                break
                    except AttributeError:
                        # Not a log function
                        return


def register(linter):
    """Required method to auto register this checker."""
    linter.register_checker(VirtChecker(linter))
