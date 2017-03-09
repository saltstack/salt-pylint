# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import
from lib2to3.fixes import fix_imports as lib2to3_fix_imports

# Import 3rd-party libs
import six
from libmodernize.fixes import fix_imports_six as libmodernize_fix_imports

MAPPING = {}

for key, value in six.iteritems(libmodernize_fix_imports.FixImportsSix.mapping):
    MAPPING[key] = 'salt.ext.{0}'.format(value)


class FixImportsSaltSix(lib2to3_fix_imports.FixImports):

    mapping = MAPPING
