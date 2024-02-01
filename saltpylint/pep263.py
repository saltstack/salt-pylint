# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Henrik Holmboe (henrik@holmboe.se)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    ======================
    PEP-263 PyLint Checker
    ======================
'''

# Import Python libs
from __future__ import absolute_import
import re
import itertools

# Import PyLint libs
from saltpylint.checkers import BaseChecker

# Import 3rd-party libs
import six


class FileEncodingChecker(BaseChecker):
    '''
    Check for PEP263 compliant file encoding in file.
    '''

    name = 'pep263'
    msgs = {'W9901': ('PEP263: Multiple file encodings',
                      'multiple-encoding-in-file',
                      ('There are multiple encodings in file.')),
            'W9902': ('PEP263: Parser and PEP263 encoding mismatch',
                      'encoding-mismatch-in-file',
                      ('The pylint parser and the PEP263 file encoding in file '
                       'does not match.')),
            'W9903': ('PEP263: Use UTF-8 file encoding',
                      'no-encoding-in-file',
                      ('There is no PEP263 compliant file encoding in file.')),
            'W9904': ('PEP263: Use UTF-8 file encoding',
                      'wrongly-encoded-file',
                      ('Change file encoding and PEP263 header in file.')),
            'W9905': ('PEP263: Use UTF-8 file encoding',
                      'no-encoding-in-empty-file',
                      ('There is no PEP263 compliant file encoding in file.')),
            }
    priority = -1
    options = ()

    RE_PEP263 = r'coding[:=]\s*([-\w.]+)'
    REQ_ENCOD = six.b('utf-8')

    def process_module(self, node):
        '''
        process a module

        the module's content is accessible via node.file_stream object
        '''
        pep263 = re.compile(six.b(self.RE_PEP263))

        try:
            file_stream = node.file_stream
        except AttributeError:
            # Pylint >= 1.8.1
            file_stream = node.stream()

        # Store a reference to the node's file stream position
        current_stream_position = file_stream.tell()

        # Go to the start of stream to achieve our logic
        file_stream.seek(0)

        # Grab the first two lines
        twolines = list(itertools.islice(file_stream, 2))
        pep263_encoding = [m.group(1).lower() for l in twolines for m in [pep263.search(l)] if m]

        multiple_encodings = len(pep263_encoding) > 1
        file_empty = len(twolines) == 0

        # Reset the node's file stream position
        file_stream.seek(current_stream_position)

        # - If the file has an UTF-8 BOM and yet uses any other
        #   encoding, it will be caught by F0002
        # - If the file has a PEP263 UTF-8 encoding and yet uses any
        #   other encoding, it will be caught by W0512
        # - If there are non-ASCII characters and no PEP263, or UTF-8
        #   BOM, it will be caught by W0512
        # - If there are ambiguous PEP263 encodings it will be caught
        #   by E0001, we still test for this
        if multiple_encodings:
            self.add_message('W9901', line=1)

        if node.file_encoding:
            pylint_encoding = node.file_encoding.lower()
            if six.PY3:
                pylint_encoding = pylint_encoding.encode('utf-8')
            if pep263_encoding and pylint_encoding not in pep263_encoding:
                self.add_message('W9902', line=1)
        if not pep263_encoding:
            if file_empty:
                self.add_message('W9905', line=1)
            else:
                self.add_message('W9903', line=1)
        elif self.REQ_ENCOD not in pep263_encoding:
            self.add_message('W9904', line=1)


def register(linter):
    '''
    required method to auto register this checker
    '''
    linter.register_checker(FileEncodingChecker(linter))
