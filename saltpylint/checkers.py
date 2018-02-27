# -*- coding: utf-8 -*-
'''
    saltpylint.checkers
    ~~~~~~~~~~~~~~~~~~~~

    Works around older astroid versions
'''
# Import python libs
from __future__ import absolute_import

# Import pylint libs
import astroid
from pylint.checkers import BaseChecker as _BaseChecker
# Imported to avoid needing a separate import from pylint.checkers
from pylint.checkers import utils


class BaseChecker(_BaseChecker):
    def __init__(self, *args, **kwargs):
        super(BaseChecker, self).__init__(*args, **kwargs)
        if hasattr(self, 'visit_call') and not hasattr(astroid, 'Call'):
            setattr(self, 'visit_callfunc', self.visit_call)

