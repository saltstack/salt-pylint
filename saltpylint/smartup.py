"""
Pylint Smartup Transformers
===========================

This plugin will register some transform functions which will allow PyLint to better
understand some classed used in Salt which trigger, `no-member` and `maybe-no-member`
A bridge between the `pep8`_ library and PyLint

"""

from astroid import MANAGER
from astroid import nodes


def rootlogger_transform(obj):
    if obj.name != "RootLogger":
        return

    def _inject_method(cls, msg, *args, **kwargs):
        pass

    if not hasattr(obj, "trace"):
        obj.trace = _inject_method

    if not hasattr(obj, "garbage"):
        obj.garbage = _inject_method


def register(linter):
    """Register the transformation functions."""
    try:
        MANAGER.register_transform(nodes.Class, rootlogger_transform)
    except AttributeError:
        MANAGER.register_transform(nodes.ClassDef, rootlogger_transform)
