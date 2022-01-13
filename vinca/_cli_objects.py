'''Simple Spaced Repetition'''

from pathlib import Path as _Path
from vinca._cardlist import Cardlist as _Cardlist
from vinca._card import Card as _Card
from vinca._config import config as _config
from vinca._generators import generators_dict as _generators_dict
from vinca._tag_caching import tags_cache as _tags_cache

# load the card generators into the module
for _hotkey, _generator_func in _generators_dict.items():
        globals()[_generator_func.__name__] = _generator_func
        globals()[_hotkey] = _generator_func

# create a collection (cardlist) out of all the cards
col = collection = _Cardlist.from_directory(_config.cards_path)
col.sort('seen')

# import some methods of the collection Cardlist object directly into the module's namespace
# this is so that ```vinca col review``` can be written as ```vinca review```
_methods = ('browse','count','filter','find','findall','purge','review','sort','time')
for _method_name in _methods:
        globals()[_method_name] = getattr(collection, _method_name)

# utility functions
help = '''\
vinca --help              general help
vinca filter --help       help on a specific subcommand
man vinca                 vinca tutorial
online man page           online_help = 'https://oscarlaird.github.io/vinca-SRS/vinca.1.html'''
# TODO create a vinca-tutor script that helps the user through a set of cards on spaced repetition
about = (_Path(__file__).parent / 'docs/about.md').read_text()
tips = (_Path(__file__).parent / 'docs/tips.md').read_text()

# quick reference to the most recent card
_lcp = _config.last_card_path
_lcp_exists = isinstance(_lcp, _Path) and _lcp.exists()
lc = last_card = _Card(path = _lcp) if _lcp_exists else 'no last card'

class advanced:
        ''' A set of rarely used advanced commands '''
        def update_tags(self):
                tags = collection.tags
                _tags_cache.update(tags)
                return tags
        from_directory = _Cardlist.from_directory
        set_cards_path = _config.set_cards_path
        cards_path = _config.cards_path

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
