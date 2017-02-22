# -*- coding: utf-8 -*-

from __future__ import absolute_import
from libmodernize.fixes import fix_dict_six


class FixDictSaltSix(fix_dict_six.FixDictSix):

    def transform(self, node, results):
        method = results['method'][0]
        method_name = method.value
        if method_name not in ('keys', 'items', 'values'):
            return self.transform_iter(method_name, node, results['head'])
