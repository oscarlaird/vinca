import re
from random import random
from shutil import copytree, rmtree
from pathlib import Path
from vinca._card import Card
from vinca._browser import Browser
from vinca._lib import ansi
from vinca._lib.vinput import VimEditor
from vinca._lib.readkey import readkey
from vinca._lib import casting
from vinca._lib.julianday import julianday
TODAY = julianday()

import sqlite3

class Cardlist:
        ''' A Cardlist is basically just an SQL query linked to a database
        The filter, sort, findall, and slice methods build up this query
        When used as an iterator it is just a list of cards (ids) 
        It is responsible for knowing its database, usually ~/cards.db '''

        def __init__(self, database):
                self.filter_query = None
                self.sort_query = None
                self.findall_query = None
                self.database = database
                self.cursor = self.database.cursor

        @property
        def full_query(self):
            pass

        def explicit_cards_list(self):
                self.cursor.execute(f'SELECT id FROM cards')
                ids = [dict(row)['id'] for row in self.cursor.fetchall()]
                return [Card(id, self.database) for id in ids]

        def __iter__(self):
                return self.explicit_cards_list().__iter__()

        def __getitem__(self, slice):
                return self.explicit_cards_list().__getitem__(slice)

        def __len__(self):
                self.cursor.execute('SELECT COUNT(*) FROM cards')
                return self.cursor.fetchone()[0]

        def __str__(self):
                s = '' # we build up our string to return
                l = len(self)
                if l == 0:
                        return 'No cards.'
                if l > 6:
                        s += f'6 of {l}\n'
                s += ansi.codes['line_wrap_off']
                for card in self.explicit_cards_list()[:6]:
                    if card.due_as_of(TODAY):
                            s += ansi.codes['blue']
                    if card['deleted']:
                            s += ansi.codes['red']
                    s += f'{card}\n'
                    s += ansi.codes['reset']
                s += ansi.codes['line_wrap_on']
                return s

        def browse(self):
                ''' Interactively manage you collection. See the tutorial (man vinca) for help. '''
                Browser(self.explicit_cards_list()).browse()

        def review(self):
                ''' Review your cards. '''
                self.filter(due = True)
                Browser(self.explicit_cards_list()).review()
                                
        def add_tag(self, tag):
                ' Add a tag to cards '
                for card in self:
                        card.tags += [tag]

        def remove_tag(self, tag):
                ' Remove a tag from cards '
                for card in self:
                        if tag in card.tags:
                                card.tags.remove(tag)
                        # TODO do this with set removal
                        card.save_metadata()  # metadata ops should be internal TODO

        def tags(self):
                raise NotImplementedError
                return set([tag for card in self for tag in card.tags])

        def count(self):
                ''' simple summary statistics '''
                return {'total': len(self)}


        def postpone(self, n=1):
                'Make cards due n days after today. (default 1)'
                raise NotImplementedError
                for card in self:
                        card.postpone(n=n)
                print(f'{len(self)} cards postponed.')

        def delete(self):
                'delete cards'
                self.cursor.execute('UPDATE cards SET deleted = True FROM temptable WHERE cards.id = temptable.id')
                print(f'{len(self)} cards deleted')

        def restore(self):
                'restore (undelete) cards'
                self.cursor.execute('UPDATE cards SET deleted = False FROM temptable WHERE cards.id = temptable.id')
                print(f'{len(self)} cards restored')


        def filter(self, *,
                   tag = None,
                   created_after=None, created_before=None,
                   seen_after=None, seen_before=None,
                   due_after=None, due_before=None,
                   editor=None, reviewer=None,
                   deleted=False, due=False, new=False,
                   invert=False):
                ''' Filter the collection. Try `vinca filter` (without arguments) for usage examples. '''

                # cast dates to dates
                created_after = casting.to_date(created_after)
                created_before = casting.to_date(created_before)
                seen_after = casting.to_date(seen_after)
                seen_before = casting.to_date(seen_before)
                due_after = casting.to_date(due_after)
                due_before = casting.to_date(due_before)

                # assert that at least one filter predicate has been specified
                if not any((tag,
                   created_after, created_before,
                   seen_after, seen_before,
                   due_after, due_before,
                   editor, reviewer,
                   deleted, due, new)):
                        print('Examples:\n'
                              'vinca filter --new                       New Cards\n'
                              'vinca filter --editor verses             Poetry Cards\n'
                              'vinca filter --created-after -7          Cards created in the last week.\n'
                              '\n'
                              'Consult `vinca filter --help` for a complete list of predicates')
                        return


                
                if due: due_before = TODAY

                f = lambda card: (((not tag or tag in card.tags) and
                                (not created_after or created_after <= card.create_date) and
                                (not created_before or created_before >= card.create_date) and 
                                (not seen_after or seen_after <= card.seen_date) and
                                (not seen_before or seen_before >= card.seen_date) and 
                                (not due_after or due_after <= card.due_date) and
                                (not due_before or due_before >= card.due_date) and 
                                (not editor or editor == card.editor) and
                                (not reviewer or reviewer == card.reviewer) and
                                (not deleted or card.deleted ) and
                                (not new or card.new)) ^
                                invert)
                
                return self.__class__([c for c in self if f(c)])

        def find(self, pattern):
                ''' return the first card containing a search pattern '''
                matches = self.findall(pattern)
                matches.sort(criterion = 'seen')
                return matches[0] if matches else 'no match found'

        def findall(self, pattern):
                ''' return all cards containing a search-pattern '''
                try:
                        p = re.compile(f'({pattern})')  # wrap in parens to create regex group \1
                except re.error:
                        print(f'The pattern {p} is invalid regex')
                        return
                contains_pattern = lambda card: p.search(card.string)
                return self.__class__([c for c in self if contains_pattern(c)])

        def sort(self, criterion=None, *, reverse=False):
                ''' sort the collection. criterion
                should be (due | seen | created | time | random) '''
                crit_dict = {
                        'due': lambda card: card.due_date,
                        'seen': lambda card: card.seen_date,
                        'created': lambda card: card.create_date,
                        'time': lambda card: card.time,
                        'random': lambda card: random()} # random sort
                # E.g. we want to see the cards that have taken the most time first
                if criterion not in crit_dict:
                        print('supply a sort criterion: (due | seen | created | time | random)')
                        exit()
                # For some criteria it is natural to see the highest value first
                # switch reverse boolean flag iff it is a reverse crit
                reverse ^= criterion in ('created', 'seen', 'time') 
                sort_function = crit_dict[criterion]
                self._cards.sort(key = sort_function, reverse = reverse)
                return self

        def time(self):
                ''' Total time spend studying these cards. '''
                raise NotImplementedError

