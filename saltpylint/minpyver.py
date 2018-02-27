# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2015 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    ===============================================
    PyLint Minimum Python Version Enforcing Checker
    ===============================================

    PyLint plugin which checks if the code meet the requirements of a targeted
    minimal version.
'''

# Import Python libs
from __future__ import absolute_import

# Import PyLint libs
from pylint.interfaces import IRawChecker
from saltpylint.checkers import BaseChecker

# Import 3rd-party libs
try:
    from saltpylint.ext import pyqver2
    HAS_PYQVER = True
except ImportError:
    import warnings  # pylint: disable=wrong-import-order
    warnings.warn(
        'Unable to import saltpylint.ext.pyqver. Running on Python 3? Checker skipped.',
        RuntimeWarning
    )
    HAS_PYQVER = False


class MininumPythonVersionChecker(BaseChecker):
    '''
    Check the minimal required python version
    '''

    __implements__ = IRawChecker

    name = 'mininum-python-version'
    msgs = {'E0598': ('Incompatible Python %s code found: %s',
                      'minimum-python-version',
                      'The code does not meet the required minimum python version'),
           }

    priority = -1

    options = (('minimum-python-version',
                {'default': '2.6', 'type': 'string', 'metavar': 'MIN_PYTHON_VERSION',
                 'help': 'The desired minimum python version to enforce. Default: 2.6'}
               ),
              )

    def process_module(self, node):
        '''
        process a module
        '''
        if not HAS_PYQVER:
            return

        minimum_version = tuple([int(x) for x in self.config.minimum_python_version.split('.')])
        with open(node.path, 'r') as rfh:
            for version, reasons in pyqver2.get_versions(rfh.read()).iteritems():
                if version > minimum_version:
                    for lineno, msg in reasons:
                        self.add_message(
                            'E0598', line=lineno,
                            args=(self.config.minimum_python_version, msg)
                        )


def register(linter):
    '''
    required method to auto register this checker
    '''
    linter.register_checker(MininumPythonVersionChecker(linter))
