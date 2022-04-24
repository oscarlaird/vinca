'''Simple Spaced Repetition'''

from pathlib import Path as _Path
from vinca._cardlist import Cardlist as _Cardlist
from vinca._config import collection_path
# from vinca._generators import generators_dict as _generators_dict

# load the card generators into the module
# for _hotkey, _generator_func in _generators_dict.items():
        # globals()[_generator_func.__name__] = _generator_func
        # globals()[_hotkey] = _generator_func

# create a collection (cardlist) out of all the cards
col = collection = _Cardlist(collection_path)

# import some methods of the collection Cardlist object directly into the module's namespace
# this is so that ```vinca col review``` can be written as ```vinca review```
# _methods = ('browse','count','filter','find','findall','purge','review','sort','time')
_methods = ('count',)
for _method_name in _methods:
        globals()[_method_name] = getattr(collection, _method_name)

# utility functions
# TODO create a vinca-tutor script that helps the user through a set of cards on spaced repetition
about = (_Path(__file__).parent / 'docs/about.txt').read_text()
tips = (_Path(__file__).parent / 'docs/tips.txt').read_text()
help = (_Path(__file__).parent / 'docs/help.txt').read_text()

# # quick reference to the most recent card
# _lcp = _config.last_card_path
# _lcp_exists = isinstance(_lcp, _Path) and _lcp.exists()
# lc = last_card = _Card(path = _lcp) if _lcp_exists else 'no last card'
# 
# class advanced:
#         ''' A set of rarely used advanced commands '''
#         def update_tags(self):
#                 tags = collection.tags
#                 _tags_cache.update(tags)
#                 return tags
#         from_directory = _Cardlist.from_directory
#         set_cards_path = _config.set_cards_path
#         cards_path = _config.cards_path

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
