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

# Import Python libs
from __future__ import absolute_import
import os
import sys
import glob
import stat

# Import PyLint libs
from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker


class FilePermsChecker(BaseChecker):
    '''
    Check for files with undesirable permissions
    '''

    __implements__ = IRawChecker

    name = 'fileperms'
    msgs = {'E0599': ('Module file has the wrong file permissions(expected %s): %s',
                      'file-perms',
                      ('Wrong file permissions')),
           }

    priority = -1

    options = (('fileperms-default',
                {'default': '0644', 'type': 'string', 'metavar': 'ZERO_PADDED_PERM',
                 'help': 'Desired file permissons. Default: 0644'}
               ),
               ('fileperms-ignore-paths',
                {'default': (), 'type': 'csv', 'metavar': '<comma-separated-list>',
                 'help': 'File paths to ignore file permission. Glob patterns allowed.'}
               )
              )

    def process_module(self, node):
        '''
        process a module
        '''

        for listing in self.config.fileperms_ignore_paths:
            if node.file.split('{0}/'.format(os.getcwd()))[-1] in glob.glob(listing):
                # File is ignored, no checking should be done
                return

        desired_perm = self.config.fileperms_default
        desired_perm = desired_perm.strip('"').strip('\'').lstrip('0').zfill(4)
        if desired_perm[0] != '0':
            # Always include a leading zero
            desired_perm = '0{0}'.format(desired_perm)

        if sys.version_info < (3,):
            module_perms = str(oct(stat.S_IMODE(os.stat(node.file).st_mode)))
        else:
            # The octal representation in python 3 has changed to 0o644 instead of 0644
            if desired_perm[1] != 'o':
                desired_perm = '0o' + desired_perm[1:]
            module_perms = oct(stat.S_IMODE(os.stat(node.file).st_mode))
        if module_perms != desired_perm:
            self.add_message('E0599', line=1, args=(desired_perm, module_perms))


def register(linter):
    '''
    required method to auto register this checker
    '''
    linter.register_checker(FilePermsChecker(linter))
