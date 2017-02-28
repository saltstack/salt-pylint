# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2017 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    saltpylint.salttesting
    ~~~~~~~~~~~~~~~~~~~~~~

    Checks blacklisted salttesting usage
'''

# Import python libs
from __future__ import absolute_import
import os
import fnmatch

# Import pylint libs
import astroid
from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker
from pylint.checkers.utils import check_messages

MSGS = {
    'W8402': ('Uses of a blacklisted module %r: %s',
              'blacklisted-module',
              'Used a module marked as blacklisted is imported.'),
    'W8403': ('Uses of a blacklisted import %r: %s',
              'blacklisted-import',
              'Used an import marked as blacklisted.'),
    'W8404': ('Uses of blacklisted test module execution code: %s',
              'blacklisted-test-module-execution',
              'Uses of blacklisted test module execution code.'),
    'W8405': ('Uses of blacklisted sys.path updating through \'ensure_in_syspath\'. '
              'Please remove the import and any calls to \'ensure_in_syspath()\'.',
              'blacklisted-syspath-update',
              'Uses of blacklisted sys.path updating through ensure_in_syspath.'),
    }


class BlacklistedImportsChecker(BaseChecker):

    __implements__ = IAstroidChecker

    name = 'blacklisted-imports'
    msgs = MSGS
    priority = -2

    options = (
        ('blacklisted-modules', {
            'default': ('salttesting', 'integration', 'unit'),
            'type': 'csv',
            'metavar': '<modules>',
            'help': 'Blacklisted modules which should not be used, separated by a comma'}),
    )

    @check_messages('blacklisted-imports')
    def visit_import(self, node):
        """triggered when an import statement is seen"""
        module_filename = self._get_node_source_filename(node)
        if module_filename and not fnmatch.fnmatch(module_filename, 'test_*.py*'):
            return
        modnode = node.root()
        names = [name for name, _ in node.names]

        for name in names:
            self._check_blacklisted_module(node, name)

    @check_messages('blacklisted-imports')
    def visit_importfrom(self, node):
        """triggered when a from statement is seen"""
        module_filename = self._get_node_source_filename(node)
        if module_filename and not fnmatch.fnmatch(module_filename, 'test_*.py*'):
            return
        basename = node.modname
        self._check_blacklisted_module(node, basename)

    def _check_blacklisted_module(self, node, mod_path):
        """check if the module is blacklisted"""
        for mod_name in self.config.blacklisted_modules:
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
                    if import_from_module == 'salttesting.mock':
                        for name in names:
                            msg = 'Please use \'from tests.support.mock import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if names:
                        for name in names:
                            if name in ('TestLoader', 'TextTestRunner',  'TestCase', 'expectedFailure',
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
                                            'CONF_DIR',
                                            'PILLAR_DIR',
                                            'TMP_SCRIPT_DIR',
                                            'ENGINES_DIR',
                                            'LOG_HANDLERS_DIR'):
                                    msg = 'Please use \'from tests.support.paths import {0}\''.format(name)
                                    self.add_message('blacklisted-import', node=node, args=(mod_path, msg))
                                    continue
                                msg = 'Please use \'from tests.{0} import {1}\''.format(mod_name, name)
                                self.add_message('blacklisted-import', node=node, args=(mod_path, msg))
                                continue
                            msg = 'Please report this error to SaltStack so we can fix it: Trying to import {0} from {1}'.format(name, mod_name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                except AttributeError:
                    if mod_name in ('integration', 'unit'):
                        msg = 'Please use \'import tests.{0} as {0}\''.format(mod_name)
                        self.add_message('blacklisted-import', node=node, args=(mod_path, msg))
                        continue
                    msg = 'Please report this error to SaltStack so we can fix it: Trying to import {0}'.format(mod_name)
                    self.add_message('blacklisted-import', node=node, args=(mod_path, msg))

    def _get_node_source_filename(self, node):
        levels = 10
        parent = node
        while True:
            if parent is None:
                break
            if isinstance(parent, astroid.Module):
                break
            if not levels:
                break
            levels -= 1
            parent = node.parent
        try:
            module_filename = os.path.basename(parent.source_file)
            return module_filename
        except AttributeError:
            return


def register(linter):
    """required method to auto register this checker """
    linter.register_checker(BlacklistedImportsChecker(linter))
