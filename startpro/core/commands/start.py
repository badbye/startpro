# encoding: utf-8

"""
Created on 2014.05.26

@author: Allen
"""
import sys
from importlib import import_module

from startpro.core.topcmd import TopCommand
from startpro.core.utils.loader import get_script_name
from startpro.core.utils.opts import load_script_temp, get_exec_func

options = {"-full": "if need full path name of script"}


class Command(TopCommand):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """

    def run(self, **kwargs):
        script_name, script = get_script_name()
        mod = import_module(script['path'])
        func = get_exec_func(mod=mod, name=script_name, is_class=script['is_class'])
        func(**kwargs)

    def help(self, **kwargvs):
        print('Start a program.')
        print('')
        print("Available options:")
        for name, desc in sorted(options.items()):
            print("  %-13s %s" % (name, desc))
