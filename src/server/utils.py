#!/usr/bin/env python3
'''
'''

import logging
import argparse

_LC = logging.getLoggerClass()

class ContextManager(object):
    '''\
    Mixin class to provide common context manager interface
    with silent close, exception propagation, and logging.
    '''

    def __enter__(self):
        if hasattr(self, 'log') and isinstance(self.log, _LC):
            self.log.debug('%s: enter', self.__class__.__name__)
        return self

    def __exit__(self, xt, xv, tb):
        if hasattr(self, 'log') and isinstance(self.log, _LC):
            self.log.debug('%s: exit', self.__class__.__name__)

        if hasattr(self, 'close') and callable(self.close):
            try:
                self.close()
            except:
                pass
        if xv:
            if hasattr(self, 'log') and isinstance(self.log, _LC):
                self.log.error('%s: %r', self.__class__.__name__, xv, exc_info=1)
            raise xv
#end class ContextManager

class Namespace(object):
    '''\
    Generic namespace.
    Allow for .name access to the items.
    Somehow mimics generic dict interface.
    '''

    def __init__(self, *av, **kw):
        self._namespace = dict()
        for x in av:
            self._namespace.update(x)
        self._namespace.update(kw)

    def update(self, data):
        if isinstance(data, Namespace):
            self._namespace.update(data._namespace)
        else:
            self._namespace.update(data)
        return self

    def __getattribute__(self, name):
        if name.startswith('_'):
            return super(Namespace, self).__getattribute__(name)
        if name in self._namespace:
            return self._namespace[name]
        raise AttributeError('{!r} has no attribute {!r}'.format(
                             self.__class__.__name__, name))

    def __contains__(self, what):
        return what in self._namespace

#end class Namespace

class AP(argparse.ArgumentParser):
    '''\
    Handy argument parser.
    Example use:
        args = AP(...).add('--arg1', ...).add('--arg2', ...).end_of_args()
        if args.arg2: ...
    '''

    def __init__(self, *av, **kw):
        super(AP, self).__init__(*av, **kw)

    def add(self, *av, **kw):
        self.add_argument(*av, **kw)
        return self

    def end_of_args(self):
        return self.parse_args()
#end class AP


# vim: set ft=python ai et ts=4 sts=4 sw=4 colorcolumn=80: #
