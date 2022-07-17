"""Spaced Repetition CLI"""

import sqlite3 as _sqlite3
from vinca_CLI._CLI_cardlist import CLI_Cardlist as _CLI_Cardlist
from vinca_CLI._config import collection_path, __file__ as _config_file
from vinca_CLI._sync import Sync as _Sync
from pathlib import Path as _Path

from rich import print as _print

collection_path = _Path(collection_path).expanduser()
_vinca_path = _Path(__file__).parent
_empty_deck_path = _vinca_path / 'empty_deck.db'
_tutorial_path = _vinca_path / 'tutorial_cards.db'

# create a collection if it does not exist
if not collection_path.exists():
        print(f'no collection found at {collection_path}')
        import shutil
        shutil.copy(_empty_deck_path, collection_path)
        print('empty collection created')

# create collection to db
_cursor = _sqlite3.connect(collection_path).cursor()

# sync interface for the cli
sync = _Sync(_cursor)

_all_cards = _CLI_Cardlist(_cursor)
globals()['-a'] = _all_cards
col = _all_cards
col = col.filter(tag = 'private', invert = True)

# The "tutorial" is just a deck of cards used to teach the basics of vinca
_tutorial_cursor = _sqlite3.connect(_tutorial_path).cursor()
tutorial = _CLI_Cardlist(_tutorial_cursor)

# import some methods of the collection Cardlist object directly into the module's namespace
# this is so that ```vinca col review``` can be written as ```vinca review```
_methods = ('browse', 'count', 'filter', 'find', 'findall', 'review', 'sort', 'purge', 'basic', 'verses', 'stats')
for _method_name in _methods:
    globals()[_method_name] = getattr(col, _method_name)

globals()['1'] = lambda: col[1]
globals()['1'].__doc__ = "most recent card"
globals()['2'] = lambda: col[2]
globals()['2'].__doc__ = "second most recent card"
globals()['3'] = lambda: col[3]
globals()['3'].__doc__ = "third most recent card"


def edit_config():
    from subprocess import run
    run(['vim', _config_file])


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
