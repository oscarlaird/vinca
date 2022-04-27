'''Simple Spaced Repetition'''

from pathlib import Path as _Path
from vinca._cardlist import Cardlist as _Cardlist
from vinca._config import collection_path
import _sqlite3

_cursor = _sqlite3.connect(collection_path).cursor()

# create a collection (cardlist) out of all the cards
col = collection = _Cardlist(_cursor)

# import some methods of the collection Cardlist object directly into the module's namespace
# this is so that ```vinca col review``` can be written as ```vinca review```
_methods = ('browse','count','filter','find','findall','review','sort','time')
for _method_name in _methods:
        globals()[_method_name] = getattr(collection, _method_name)

for i in range(1,4):
        globals()[str(i)] = collection[i]
del i

# utility functions
# TODO create a vinca-tutor script that helps the user through a set of cards on spaced repetition
# about = (_Path(__file__).parent / 'docs/about.txt').read_text()
# tips = (_Path(__file__).parent / 'docs/tips.txt').read_text()
# help = (_Path(__file__).parent / 'docs/help.txt').read_text()
examples = 'TODO' #TODO

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
