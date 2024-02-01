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
from saltpylint.checkers import BaseChecker


class FilePermsChecker(BaseChecker):
    '''
    Check for files with undesirable permissions
    '''

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
        if '-' in desired_perm:
            desired_perm = desired_perm.split('-')
        else:
            desired_perm = [desired_perm]

        if len(desired_perm) > 2:
            raise RuntimeError('Permission ranges should be like XXXX-YYYY')

        for idx, perm in enumerate(desired_perm):
            desired_perm[idx] = desired_perm[idx].strip('"').strip('\'').lstrip('0').zfill(4)
            if desired_perm[idx][0] != '0':
                # Always include a leading zero
                desired_perm[idx] = '0{0}'.format(desired_perm[idx])
            if sys.version_info > (3,):
                # The octal representation in python 3 has changed to 0o644 instead of 0644
                if desired_perm[idx][1] != 'o':
                    desired_perm[idx] = '0o' + desired_perm[idx][1:]
            if sys.platform.startswith('win'):
                # Windows does not distinguish between user/group/other.
                # They must all be the same. Also, Windows will automatically
                # set the execution bit on files with a known extension
                # (eg .exe, .bat, .com). So we cannot reliably test the
                # execution bit on other files such as .py files.
                user_perm_noexec = int(desired_perm[idx][-3])
                if user_perm_noexec % 2 == 1:
                    user_perm_noexec -= 1
                desired_perm[idx] = desired_perm[idx][:-3] + (str(user_perm_noexec) * 3)

        module_perms = oct(stat.S_IMODE(os.stat(node.file).st_mode))
        if sys.version_info < (3,):
            module_perms = str(module_perms)

        if len(desired_perm) == 1:
            if module_perms != desired_perm[0]:
                if sys.platform.startswith('win'):
                    # Check the variant with execution bit set due to the
                    # unreliability of checking the execution bit on Windows.
                    user_perm_noexec = int(desired_perm[0][-3])
                    desired_perm_exec = desired_perm[0][:-3] + (str(user_perm_noexec + 1) * 3)
                    if module_perms == desired_perm_exec:
                        return
                self.add_message('E0599', line=1, args=(desired_perm[0], module_perms))
        else:
            if module_perms < desired_perm[0] or module_perms > desired_perm[1]:
                if sys.platform.startswith('win'):
                    # Check the variant with execution bit set due to the
                    # unreliability of checking the execution bit on Windows.
                    user_perm_noexec0 = int(desired_perm[0][-3])
                    desired_perm_exec0 = desired_perm[0][:-3] + (str(user_perm_noexec0 + 1) * 3)
                    user_perm_noexec1 = int(desired_perm[1][-3])
                    desired_perm_exec1 = desired_perm[1][:-3] + (str(user_perm_noexec1 + 1) * 3)
                    if desired_perm_exec0 <= module_perms <= desired_perm_exec1:
                        return
                desired_perm = '>= {0} OR <= {1}'.format(*desired_perm)
                self.add_message('E0599', line=1, args=(desired_perm, module_perms))


def register(linter):
    '''
    required method to auto register this checker
    '''
    linter.register_checker(FilePermsChecker(linter))
