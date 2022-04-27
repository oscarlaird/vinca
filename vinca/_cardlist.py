from pathlib import Path
from vinca._card import Card
from vinca._browser import Browser
from vinca._lib import ansi
from vinca._lib.vinput import VimEditor
from vinca._lib.readkey import readkey
from vinca._lib.julianday import today
TODAY = today()

import sqlite3

class Cardlist:
        ''' A Cardlist is basically just an SQL query linked to a database
        The filter, sort, findall, and slice methods build up this query
        When used as an iterator it is just a list of cards (ids) 
        It is responsible for knowing its database, usually ~/cards.db '''

        def __init__(self, cursor):
                # TODO we should receive a cursor only
                # (I can use cursor.connection...)
                # TODO TODO because Cardlists are so cheap,
                # my functions should just return a modified copy, not self.
                self._conditions = ['TRUE']
                self._ORDER_BY = ' ORDER BY (select max(date) from reviews where reviews.card_id=cards.id)'
                self._cursor = cursor

        @property
        def _SELECT_IDS(self):
                ' SQL Query of all card IDs. Check this first when debugging. '
                return 'SELECT id FROM cards' + self._WHERE + self._ORDER_BY

        @property
        def _WHERE(self):
                return ' WHERE ' + ' AND '.join(self._conditions)

        def explicit_cards_list(self, LIMIT = 1000):
                self._cursor.execute(self._SELECT_IDS + f' LIMIT {LIMIT}')
                ids = [row[0] for row in self._cursor.fetchall()]
                return [Card(id, self._cursor) for id in ids]

        def __getitem__(self, arg):
                # access cards by their index
                # we use human-oriented indexing beginning with 1...
                if type(arg) is slice:
                        idx = arg.stop 
                elif type(arg) is int:
                        idx = arg
                else:
                        raise ValueError
                self._cursor.execute(self._SELECT_IDS + f' LIMIT 1 OFFSET {idx - 1}')
                card_id = self._cursor.fetchone()[0]
                return Card(card_id, self._cursor)

        def __len__(self):
                self._cursor.execute(f'SELECT COUNT(*) FROM ({self._SELECT_IDS})')
                return self._cursor.fetchone()[0]

        def __str__(self):
                sample_cards = self.explicit_cards_list(LIMIT=6)
                l = len(self)
                s = 'No cards.' if not l else f'6 of {l}\n' if l>6 else ''
                s += ansi.codes['line_wrap_off']
                s += '\n'.join([str(card) for card in sample_cards])
                s += ansi.codes['line_wrap_on']
                return s

        def browse(self):
                ''' interactively manage you collection '''
                Browser(self.explicit_cards_list()).browse()

        def review(self):
                ''' review your cards '''
                self.filter(due = True)
                Browser(self.explicit_cards_list()).review()
                                
        def add_tag(self, tag):
                ' add a tag to cards '
                raise NotImplementedError

        def remove_tag(self, tag):
                ' remove a tag from cards '
                raise NotImplementedError

        def tags(self):
                ' all tags in this cardlist '
                self._cursor.execute(f'SELECT tag FROM tags JOIN '
                    '({self._SELECT_IDS}) ON tags.card_id=id GROUP BY tag')
                return [row[0] for row in self._cursor.fetchall()]

        def count(self):
                ''' simple summary statistics '''
                total = len(self)
                self.filter(due=True)
                due = len(self)
                self.filter(due=False, new=True)
                new = len(self)
                return {'total': total,
                        'due': due,
                        'new': new}

        def postpone(self, n=1):
                'reschedule cards n days after today (default 1)'
                raise NotImplementedError

        def filter(self, *,
                   tag = None,
                   created_after=0, created_before=0,
                   due_after=0, due_before=0,
                   deleted=False, due=False, new=False, verses=False,
                   invert=False):
                ''' filter the collection '''

                parameters_conditions = (
                        # tag
                        (tag, f"(SELECT true FROM tags WHERE card_id=cards.id"),
                        # date conditions
                        (created_after, f"create_date > {TODAY + created_after}"),
                        (created_before, f"create_date < {TODAY + created_before}"),
                        (due_after, f"due_date > {TODAY + due_after}"),
                        (due_before, f"due_date < {TODAY + due_before}"),
                        # boolean conditions
                        (due, f"due_date < {TODAY}"),
                        (deleted, f"deleted = 1"),
                        (verses, f"verses = 1"),
                        (new, f"due_date = create_date"),
                )

                # assert that at least one filter predicate has been specified
                parameters = [p for p,c in parameters_conditions]
                if not any(parameters):
                        print('Examples:\n'
                            'filter --new                  new cards\n'
                            'filter --editor verses        poetry cards\n'
                            'filter --created-after -7     created in the last week\n'
                            '\n'
                            'Read `filter --help` for a complete list of predicates')
                        return

                for parameter, condition in parameters_conditions:
                        if parameter:
                                n = 'NOT ' if invert else ''
                                self._conditions.append(n + condition)
                return self

        def find(self, pattern):
                ''' return the first card containing a search pattern '''
                self.findall(pattern)
                id = self._cursor.execute(self._SELECT_IDS + ' LIMIT 1').fetchone()[0]
                return Card(id, self._cursor)



        def findall(self, pattern):
                ''' return all cards containing a search pattern '''
                self._conditions += [f"front_text LIKE '%{pattern}%' OR back_text LIKE '%{pattern}%'"]
                return self

        def sort(self, criterion=None, *, reverse=False):
                ''' sort the collection: [due | seen | created | time | random] '''
                # E.g. we want to see the cards that have taken the most time first
                        
                crit_dict = {'due': ' ORDER BY due_date',
                             'created': ' ORDER BY create_date',
                             'random': ' ORDER BY RANDOM()',
                             'time': ' ORDER BY (select sum(seconds) from reviews where reviews.card_id=cards.id)',
                             'seen': ' ORDER BY (select max(date) from reviews where reviews.card_id=cards.id)',
                              }
                if criterion not in crit_dict:
                        print(f'supply a criterion: {" | ".join(crit_dict.keys())}')
                        exit()
                self._ORDER_BY = crit_dict[criterion]
                # Sometimes it is natural to see the highest value first by default
                reverse ^= criterion in ('created', 'seen', 'time') 
                direction = ' DESC' if reverse else ' ASC'
                self._ORDER_BY += direction
                return self
                

        def time(self):
                ''' total time spend studying these cards '''
                self._cursor.execute(f'SELECT sum(seconds) FROM ({self._SELECT_IDS})'
                        ' LEFT JOIN reviews ON id=card_id')
                return self._cursor.fetchone()[0]
