"""
module docstring here
"""

from os import path
import sys
from importlib import import_module

scriptdir, scriptname = path.split(__file__)
testdir = path.split(path.abspath(__file__))[0]
mainpath = path.split(testdir)[0]
codenav_path = path.join(mainpath, "src", "codenav")
sys.path.insert(0, path.join(mainpath, "src"))
cn = import_module("codenav")
cn.cli_main()
