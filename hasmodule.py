#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for an installed module: hasmodule.py <module_name>
The result is 0 if the module is installed, and non-zero if not (or if
you don't specify a parameter)--therefore it is close to and possibly
equivalent to: python -c "import <module_name>".
"""
import sys
import subprocess
import pkg_resources
# See <https://stackoverflow.com/questions/44210656/how-to-check-if-a-
# module-is-installed-in-python-and-if-not-install-it-within-t>

if len(sys.argv) < 2:
    exit(1)

require = sys.argv[1].strip()

if len(require) < 1:
    exit(1)

installed = {pkg.key for pkg in pkg_resources.working_set}

if require not in installed:
    # python = sys.executable
    # subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    exit(1)
exit(0)
