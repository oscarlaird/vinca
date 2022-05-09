"""Spaced Repetition CLI"""

import sqlite3 as _sqlite3
from vinca._cardlist import Cardlist as _Cardlist
from vinca._config import collection_path, __file__
from pathlib import Path as _Path

from rich import print as _print

# create a collection (cardlist) out of all the cards
_cursor = _sqlite3.connect(collection_path).cursor()
col = collection = _Cardlist(_cursor)

# The "tutorial" is just a deck of cards used to teach the basics of vinca
_tutorial_path = _Path(__file__).parent / 'tutorial_cards.db'
_tutorial_cursor = _sqlite3.connect(_tutorial_path).cursor()
tutorial = _Cardlist(_tutorial_cursor)

# import some methods of the collection Cardlist object directly into the module's namespace
# this is so that ```vinca col review``` can be written as ```vinca review```
_methods = ('browse', 'count', 'filter', 'find', 'findall', 'review', 'sort', 'time', 'purge', 'basic', 'verses')
for _method_name in _methods:
    globals()[_method_name] = getattr(collection, _method_name)

globals()['1'] = lambda: collection[1]
globals()['1'].__doc__ = "most recent card"
globals()['2'] = lambda: collection[2]
globals()['2'].__doc__ = "second most recent card"
globals()['3'] = lambda: collection[3]
globals()['3'].__doc__ = "third most recent card"


def edit_config():
    from subprocess import run
    run(['vim', __file__])


def help():
    """print basic help"""
    _print('\n',
           '[bold green] --help                ', 'full screen help                        \n',
           '[bold green] basic                 ', 'create question and answer cards        \n',
           '[bold green] review                ', 'study your cards                        \n',
           '[bold green] browse                ', 'interactively manage your cards         \n',
           '[bold green] count                 ', 'simple summary statistics               \n',
           '[bold green] tutorial review       ', 'study a tutorial deck of twenty cards   \n', sep='')


globals()['-h'] = help
