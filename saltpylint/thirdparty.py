# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2017 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    saltpylint.thirdparty
    ~~~~~~~~~~~~~~~~~~~~~

    Checks all imports against a list of known and allowed 3rd-party modules
    and raises a lint error if an import not in that known 3rd-party modules list
    is not gated.
'''

# Import python libs
from __future__ import absolute_import
import os

# Import pylint libs
import astroid
import astroid.exceptions
from astroid.modutils import is_relative, is_standard_module
from pylint.interfaces import IAstroidChecker
from saltpylint.checkers import BaseChecker, utils

MSGS = {
    'W8410': ('3rd-party module import is not gated in a try/except: %r',
              '3rd-party-module-not-gated',
              '3rd-party module imported without being gated in a try/except.'),
    'C8410': ('3rd-party local module import is not gated in a try/except: %r. '
              'Consider importing at the module global scope level and gate it '
              'in a try/except.',
              '3rd-party-local-module-not-gated',
              '3rd-party module locally imported without being gated. Consider importing '
              'at the module global scope level and gate it in a try/except'),
    }


def get_import_package(modname):
    '''
    Return the import package.

    Given modname is 'salt.utils', returns 'salt'
    '''
    return modname.split('.')[0]


class ThirdPartyImportsChecker(BaseChecker):

    __implements__ = IAstroidChecker

    name = '3rd-party-imports'
    msgs = MSGS
    priority = -2

    options = (
        ('allowed-3rd-party-modules', {
            'default': (),
            'type': 'csv',
            'metavar': '<3rd-party-modules>',
            'help': 'Known 3rd-party modules which don\' require being gated, separated by a comma'}),
    )

    known_py2_modules = ('__builtin__', 'exceptions')
    known_py3_modules = ('ipaddress', 'builtins')
    known_common_std_modules = ('__future__',)
    known_std_modules = known_py2_modules + known_py3_modules + known_common_std_modules

    def __init__(self, linter=None):
        BaseChecker.__init__(self, linter)
        self._inside_try_except = False
        self._inside_funcdef = False
        self._inside_if = False
        self.cwd = self.allowed_3rd_party_modules = None

    def open(self):
        super(ThirdPartyImportsChecker, self).open()
        self.cwd = os.getcwd()
        self.allowed_3rd_party_modules = set(self.config.allowed_3rd_party_modules)  # pylint: disable=no-member

    # pylint: disable=unused-argument
    @utils.check_messages('3rd-party-imports')
    def visit_if(self, node):
        self._inside_if = True

    @utils.check_messages('3rd-party-imports')
    def leave_if(self, node):
        self._inside_if = True

    @utils.check_messages('3rd-party-imports')
    def visit_tryexcept(self, node):
        self._inside_try_except = True

    @utils.check_messages('3rd-party-imports')
    def leave_tryexcept(self, node):
        self._inside_try_except = False

    @utils.check_messages('3rd-party-imports')
    def visit_functiondef(self, node):
        self._inside_funcdef = True

    @utils.check_messages('3rd-party-imports')
    def leave_functiondef(self, node):
        self._inside_funcdef = False
    # pylint: enable=unused-argument

    @utils.check_messages('3rd-party-imports')
    def visit_import(self, node):
        names = [name for name, _ in node.names]
        for name in names:
            self._check_third_party_import(node, name)

    @utils.check_messages('3rd-party-imports')
    def visit_importfrom(self, node):
        self._check_third_party_import(node, node.modname)

    def _check_third_party_import(self, node, modname):
        if modname in self.known_std_modules:
            # Don't even care about these
            return
        module_file = node.root().file

        if is_relative(modname, module_file):
            # Is the import relative to the curent module being checked
            return

        base_modname = modname.split('.', 1)[0]
        import_modname = modname
        while True:
            try:
                imported_module = node.do_import_module(import_modname)
                if not imported_module:
                    break
                if imported_module.file.startswith(self.cwd):
                    # This is an import to package under the project being tested
                    return
                # If we reached this far, we were able to import the module but it's
                # not considered a module from within the project being checked
                break
            except Exception:  # pylint: disable=broad-except
                # This is, for example, from salt.ext.six.moves import Y
                # Because `moves` is a dynamic/runtime module
                import_modname = import_modname.rsplit('.', 1)[0]

            if import_modname == base_modname or not import_modname:
                break

        try:
            if not is_standard_module(modname):
                if self._inside_try_except is False:
                    if get_import_package(modname) in self.allowed_3rd_party_modules:
                        return
                    if self._inside_if or self._inside_funcdef:
                        message_id = '3rd-party-local-module-not-gated'
                    else:
                        message_id = '3rd-party-module-not-gated'
                    self.add_message(message_id, node=node, args=modname)
        except astroid.exceptions.AstroidBuildingException:
            # Failed to import
            if self._inside_try_except is False:
                if get_import_package(modname) in self.allowed_3rd_party_modules:
                    return
                if self._inside_if or self._inside_funcdef:
                    message_id = '3rd-party-local-module-not-gated'
                else:
                    message_id = '3rd-party-module-not-gated'
                self.add_message(message_id, node=node, args=modname)
        except astroid.exceptions.InferenceError:
            # Failed to import
            if self._inside_try_except is False:
                if get_import_package(modname) in self.allowed_3rd_party_modules:
                    return
                if self._inside_if or self._inside_funcdef:
                    message_id = '3rd-party-local-module-not-gated'
                else:
                    message_id = '3rd-party-module-not-gated'
                self.add_message(message_id, node=node, args=modname)
        except ImportError:
            # Definitly not a standard library import
            if self._inside_try_except is False:
                if get_import_package(modname) in self.allowed_3rd_party_modules:
                    return
                if self._inside_if or self._inside_funcdef:
                    message_id = '3rd-party-local-module-not-gated'
                else:
                    message_id = '3rd-party-module-not-gated'
                self.add_message(message_id, node=node, args=modname)


def register(linter):
    '''required method to auto register this checker '''
    linter.register_checker(ThirdPartyImportsChecker(linter))
