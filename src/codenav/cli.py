# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 12:18:08 2023

@author: jkris
"""

# from argparse import ArgumentParser
from codenav import serve_app


def main():
    """Run full command line process"""
    # desc = "Web App for cleaning, searching, editing, and navigating Python code."
    # parser = ArgumentParser(prog="codenav", description=desc)
    # args = vars(parser.parse_args())
    # print(f"\nCommand Line Args:\n{args}\n")
    # args = [args[key] for key in args.keys()]
    serve_app()


if __name__ == "__main__":
    main()
