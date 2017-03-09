# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2017 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    saltpylint.blacklist
    ~~~~~~~~~~~~~~~~~~~~

    Checks blacklisted imports and code usage on salt
'''

# Import python libs
from __future__ import absolute_import
import fnmatch

# Import pylint libs
from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker
from pylint.checkers.utils import check_messages

MSGS = {
    'W8402': ('Uses of a blacklisted module %r: %s',
              'blacklisted-module',
              'Used a module marked as blacklisted is imported.'),
    'W8403': ('Uses of a blacklisted external module %r: %s',
              'blacklisted-external-module',
              'Used a module marked as blacklisted is imported.'),
    'W8404': ('Uses of a blacklisted import %r: %s',
              'blacklisted-import',
              'Used an import marked as blacklisted.'),
    'W8405': ('Uses of an external blacklisted import %r: %s',
              'blacklisted-external-import',
              'Used an external import marked as blacklisted.'),
    'W8406': ('Uses of blacklisted test module execution code: %s',
              'blacklisted-test-module-execution',
              'Uses of blacklisted test module execution code.'),
    'W8407': ('Uses of blacklisted sys.path updating through \'ensure_in_syspath\'. '
              'Please remove the import and any calls to \'ensure_in_syspath()\'.',
              'blacklisted-syspath-update',
              'Uses of blacklisted sys.path updating through ensure_in_syspath.'),
    }


class BlacklistedUsageChecker(BaseChecker):

    __implements__ = IAstroidChecker

    name = 'blacklisted-usage'
    msgs = MSGS
    priority = -2

    def open(self):
        self.blacklisted_modules = ('salttesting',
                                    'integration',
                                    'unit',
                                    'mock',
                                    'six',
                                    'distutils.version')

    @check_messages('blacklisted-usage')
    def visit_import(self, node):
        '''triggered when an import statement is seen'''
        module_filename = node.root().file
        if fnmatch.fnmatch(module_filename, '__init__.py*') and \
                not fnmatch.fnmatch(module_filename, 'test_*.py*'):
            return
        modnode = node.root()
        names = [name for name, _ in node.names]

        for name in names:
            self._check_blacklisted_module(node, name)

    @check_messages('blacklisted-usage')
    def visit_importfrom(self, node):
        '''triggered when a from statement is seen'''
        module_filename = node.root().file
        if fnmatch.fnmatch(module_filename, '__init__.py*') and \
                not fnmatch.fnmatch(module_filename, 'test_*.py*'):
            return
        basename = node.modname
        self._check_blacklisted_module(node, basename)

    def _check_blacklisted_module(self, node, mod_path):
        '''check if the module is blacklisted'''
        for mod_name in self.blacklisted_modules:
            if mod_path == mod_name or mod_path.startswith(mod_name + '.'):
                names = []
                for name, name_as in node.names:
                    if name_as:
                        names.append('{0} as {1}'.format(name, name_as))
                    else:
                        names.append(name)
                try:
                    import_from_module = node.modname
                    if import_from_module == 'salttesting.helpers':
                        for name in names:
                            if name == 'ensure_in_syspath':
                                self.add_message('blacklisted-syspath-update', node=node)
                                continue
                            msg = 'Please use \'from tests.support.helpers import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module in ('salttesting.mock', 'mock'):
                        for name in names:
                            msg = 'Please use \'from tests.support.mock import {0}\''.format(name)
                            if import_from_module == 'salttesting.mock':
                                message_id = 'blacklisted-module'
                            else:
                                message_id = 'blacklisted-external-module'
                            self.add_message(message_id, node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'salttesting.parser':
                        for name in names:
                            msg = 'Please use \'from tests.support.parser import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'salttesting.case':
                        for name in names:
                            msg = 'Please use \'from tests.support.case import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'salttesting.unit':
                        for name in names:
                            msg = 'Please use \'from tests.support.unit import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'salttesting.mixins':
                        for name in names:
                            msg = 'Please use \'from tests.support.mixins import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'six':
                        for name in names:
                            msg = 'Please use \'from salt.ext.six import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'distutils.version':
                        for name in names:
                            msg = 'Please use \'from salt.utils.versions import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if names:
                        for name in names:
                            if name in ('TestLoader', 'TextTestRunner', 'TestCase', 'expectedFailure',
                                        'TestSuite', 'skipIf', 'TestResult'):
                                msg = 'Please use \'from tests.support.unit import {0}\''.format(name)
                                self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                                continue
                            if name == 'run_tests':
                                msg = 'Please remove the \'if __name__ == "__main__":\' section from the end of the module'
                                self.add_message('blacklisted-test-module-execution', node=node, args=msg)
                                continue
                            if mod_name in ('integration', 'unit'):
                                if name in ('SYS_TMP_DIR',
                                            'TMP',
                                            'FILES',
                                            'PYEXEC',
                                            'MOCKBIN',
                                            'SCRIPT_DIR',
                                            'TMP_STATE_TREE',
                                            'TMP_PRODENV_STATE_TREE',
                                            'TMP_CONF_DIR',
                                            'TMP_SUB_MINION_CONF_DIR',
                                            'TMP_SYNDIC_MINION_CONF_DIR',
                                            'TMP_SYNDIC_MASTER_CONF_DIR',
                                            'CODE_DIR',
                                            'TESTS_DIR',
                                            'CONF_DIR',
                                            'PILLAR_DIR',
                                            'TMP_SCRIPT_DIR',
                                            'ENGINES_DIR',
                                            'LOG_HANDLERS_DIR',
                                            'INTEGRATION_TEST_DIR'):
                                    msg = 'Please use \'from tests.support.paths import {0}\''.format(name)
                                    self.add_message('blacklisted-import', node=node, args=(mod_path, msg))
                                    continue
                                msg = 'Please use \'from tests.{0} import {1}\''.format(mod_path, name)
                                self.add_message('blacklisted-import', node=node, args=(mod_path, msg))
                                continue
                            msg = 'Please report this error to SaltStack so we can fix it: Trying to import {0} from {1}'.format(name, mod_path)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                except AttributeError:
                    if mod_name in ('integration', 'unit', 'mock', 'six', 'distutils.version'):
                        if mod_name in ('integration', 'unit'):
                            msg = 'Please use \'import tests.{0} as {0}\''.format(mod_name)
                            message_id = 'blacklisted-import'
                        elif mod_name == 'mock':
                            msg = 'Please use \'import tests.support.{0} as {0}\''.format(mod_name)
                            message_id = 'blacklisted-external-import'
                        elif mod_name == 'six':
                            msg = 'Please use \'import salt.ext.{0} as {0}\''.format(name)
                            message_id = 'blacklisted-external-import'
                        elif mod_name == 'distutils.version':
                            msg = 'Please use \'import salt.utils.versions\' instead'
                            message_id = 'blacklisted-import'
                        self.add_message(message_id, node=node, args=(mod_path, msg))
                        continue
                    msg = 'Please report this error to SaltStack so we can fix it: Trying to import {0}'.format(mod_path)
                    self.add_message('blacklisted-import', node=node, args=(mod_path, msg))


def register(linter):
    '''
    Required method to auto register this checker
    '''
    linter.register_checker(BlacklistedUsageChecker(linter))
