from vinca_CLI._CLI_card import CLI_Card
from vinca_CLI._browser import Browser
from vinca_CLI._lib import ansi
from vinca_CLI._lib.readkey import readkey
from vinca_CLI._statistics import Statistics

from vinca_core.cardlist import Cardlist

import datetime

from rich import print

class CLI_Cardlist(Cardlist):


        # overwrite Cardlist methods to return CLI_Cards instead of Cards
        def explicit_cards_list(self, LIMIT = 1000):
                return [CLI_Card(card.id, card._cursor) for card in super().explicit_cards_list(LIMIT = LIMIT)]

        def __getitem__(self, arg):
                card = super().__getitem__(arg)
                return CLI_Card(card.id, card._cursor)

        def __str__(self):
                sample_cards = self.explicit_cards_list(LIMIT=6)
                l = len(self)
                s = 'No cards.' if not l else f'6 of {l}\n' if l>6 else ''
                s += ansi.codes['line_wrap_off']
                s += '\n'.join([str(card) for card in sample_cards])
                s += ansi.codes['line_wrap_on']
                return s

        def browse(self):
                """interactively manage you collection"""
                Browser(self.explicit_cards_list(), self._make_basic_card, self._make_verses_card).browse()

        def review(self):
                """review your cards"""
                due_cards = self.filter(due = True).explicit_cards_list()
                Browser(due_cards, self._make_basic_card, self._make_verses_card).review()

        def count(self):
                """simple summary statistics"""
                return {'total':  len(self),
                        'due':    len(self.filter(due=True)),
                        'new':    len(self.filter(new=True))}

        def find(self, pattern):
                """ return the first card containing a search pattern """
                try:
                        return self.findall(pattern).sort('seen')[1]
                except:
                        return f'no cards containing "{pattern}"'

        # overwrite __dir__ so that we fool python FIRE
        # we don't want methods inherited from list
        # to show up in our help message
        def __dir__(self):
                members = super().__dir__()
                hidden = ['extend','index','pop','mro','remove','append',
                          'clear','insert','reverse','copy']
                return [m for m in members if m not in hidden]

        def findall(self, pattern):
                ' alias for filter with search=pattern '
                return self.filter(search = pattern)

        def _make_basic_card(self):
                """ make a basic question and answer flashcard """
                card = CLI_Card._new_card(self._cursor)
                card.edit()
                return card
        basic = _make_basic_card

        def _make_verses_card(self):
                """ make a verses card: for recipes, poetry, oratory, instructions """
                card = CLI_Card._new_card(self._cursor)
                card.card_type = 'verses'
                card.edit()
                return card
        verses = _make_verses_card

        def delete(self):
                l = len(self)
                print(f'[bold]delete {l} cards? y/n')
                if readkey() != 'y':
                        print('[red]aborted')
                        return
                self._delete()
                print(l, 'cards deleted')

        def restore(self):
                deleted_cards = self.filter(deleted=True)
                if not deleted_cards:
                        print('none of these cards are deleted')
                count = deleted_cards._restore()
                print(count, 'cards restored')

        def purge(self, confirm=True):
                """ permanently remove deleted cards """
                deleted_cards = self.filter(deleted=True)
                n = len(deleted_cards)
                if n == 0:
                        return 'no cards to delete'
                if confirm:
                    print(f'[bold]permanently remove {len(deleted_cards)} cards?! y/n')
                    if readkey() != 'y':
                            return ('[red]aborted')
                purge_count = deleted_cards._purge() 
                return f'{purge_count} cards purged'

        def stats(self, interval=7):
                """ review statistics for the collection """
                return Statistics(self._cursor, interval=interval).print()
