# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2015 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    ====================================
    PyLint File Permissions Check Plugin
    ====================================

    PyLint plugin which checks for specific file permissions
'''

from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker
from saltpylint.ext import pyqver2


class MininumPythonVersionChecker(BaseChecker):
    '''
    Check the minimal required python version
    '''

    __implements__ = IRawChecker

    name = 'mininum-python-version'
    msgs = {'E0598': ('Incompatible Python %s code found: %s',
                      'minimum-python-version'),
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
