'''Spaced Repetition CLI'''
import sqlite3 as _sqlite3
from vinca._cardlist import Cardlist as _Cardlist
import vinca._config

# create a collection (cardlist) out of all the cards
_cursor = _sqlite3.connect(vinca._config.collection_path).cursor()
col = collection = _Cardlist(_cursor)

del vinca
# import some methods of the collection Cardlist object directly into the module's namespace
# this is so that ```vinca col review``` can be written as ```vinca review```
_methods = ('browse','count','filter','find','findall','review','sort','time','purge')
for _method_name in _methods:
        globals()[_method_name] = getattr(collection, _method_name)
basic = collection._make_basic_card
verses = collection._make_verses_card

globals()['1'] = lambda: collection[1]
globals()['1'].__doc__ = "most recent card"
globals()['2'] = lambda: collection[2]
globals()['2'].__doc__ = "second most recent card"
globals()['3'] = lambda: collection[3]
globals()['3'].__doc__ = "third most recent card"

def edit_config():
        from subprocess import run
        run(['vim', vinca._config.__file__])

'''
Add the following code to the ActionGroup object in helptext.py of fire to get proper aliasing
A better way would be to go back further into the code and check if two functions share the same id

  def Add(self, name, member=None):
    if member and member in self.members:
      dupe = self.members.index(member)
      self.names[dupe] += ', ' + name
      return
    self.names.append(name)
    self.members.append(member)
'''
'''
Make this substitution on line 458 of core.py to allow other iterables to be accessed by index

    # is_sequence = isinstance(component, (list, tuple))
    is_sequence = hasattr(component, '__getitem__') and not hasattr(component, 'values')
'''
'''
And make a corresponding change in generating the help message

  is_sequence = hasattr(component, '__getitem__') and not hasattr(component, values)
  # if isinstance(component, (list, tuple)) and component:
  if is_sequence and component:
'''
