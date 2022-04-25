from vinca._lib.vinput import VimEditor
from vinca._lib.terminal import AlternateScreen
from vinca._lib.readkey import readkey
from vinca._lib.video import DisplayImage
from vinca._lib import ansi

GRADE_DICT = {'x': 'delete', 'd': 'delete',
              'q': 'exit', '\x1b': 'exit',
              'p': 'preview', '0': 'preview',
              '1': 'again',
              '2': 'hard',
              '3': 'good', ' ': 'good', '\r': 'good', '\n': 'good',
              '4': 'easy'}

import time
from pathlib import Path
from shutil import copyfile

from vinca import _reviewers, _editors
from vinca._lib.vinput import VimEditor
from vinca._lib.julianday import julianday
TODAY = julianday()

class Card(dict):
        ''' A card is a dictionary
        its data is loaded from SQL on the fly and saved to SQL on the fly
        Card class can load without '''

        fields = ['id', 'front_text', 'back_text', 'front_image', 'back_image', 'front_audio', 'back_audio', 'verses', 'deleted', 'create_date', 'due_date', 'editing_seconds', 'reviewing_seconds', 'edit_count', 'review_count', 'stability', 'retrievability', 'tags']

        # let us access key-val pairs as simple attributes
        for f in fields:
                exec(
f'''
@property
def {f}(self):
        return self["{f}"]
@{f}.setter
def {f}(self, new_value):
        self["{f}"] = new_value
'''
)

        def __init__(self, id, database):
                self.database = database
                self.cursor =  database.cursor
                super().__init__(id = id)
                self._hotkeys = {'e': self.edit,
                                 't': self.edit_tags,
                                 'd': self.toggle_delete,
                                 'p': self.preview,
                                 '+': self.postpone,}

        def __str__(self):
                return self['front_text'] + ' | ' + self['back_text']

        def metadata(self):
                self.load_all_fields()
                return dict(self)

        def load_all_fields(self):
                # the card is normally lazy and only reads from the db if it needs to
                # here we force it to read all of its data from the db
                for f in self.fields:
                        self[f]

        def __setitem__(self, key, value):
                assert key != 'id', 'Card Id cannot be changed!'
                super().__setitem__(key, value)
                # commit change to card-dictionary to SQL database
                self.cursor.execute(f'UPDATE cards SET {key} = ? WHERE id = ?', (value, self.id))
                self.database.conn.commit()

        def __getitem__(self, key):
                if key not in self.fields:
                        raise KeyError(f'Field "{key}" does not exist')
                if key not in self.keys():
                        # load attribute from the database if we haven't yet
                        self[key] = self.cursor.execute(f'SELECT {key} FROM cards \
                                                          WHERE id = {self.id}').fetchone()[0]
                return super().__getitem__(key)

        def review(self):
                _reviewers.review(self)
                # we have probably appended a history entry
                self.save_metadata() 
                self.schedule()

        def preview(self):
                _reviewers.review(self)
                # we have probably appended a history entry
                self.undo_history()

        def edit(self):
                _editors.edit(self) 
                self.make_string()
                self.save_metadata() # we have probably modified history


        def delete(self, toggle = True):
                self.deleted = True
                return 'Card has been deleted. Use `vinca last-card restore` to undo.'

        def toggle_delete(self):
                if self.deleted:
                        self.restore()
                elif not self.deleted:
                        self.delete()

        def restore(self):
                self.deleted = False
                return 'Card restored.'

        def due_as_of(self, date):
                return self.due_date <= date

        @property
        def is_due(self):
                return self.due_as_of(TODAY)

        def edit_tags(self):
                self.tags = VimEditor(prompt = 'tags: ', text = ' '.join(self.tags), completions = tags_cache).run().split()

        def tag(self, *tags):
                ' Add tags to a card from the command line '
                self.tags += tags
                return f'card has been tagged with: {" ".join(tags)}'

        def postpone(self, n=1):
                'Make card due n days after today. (default 1)'
                tomorrow = TODAY + DAY*n
                self['due-date'] = tomorrow
                return f'Postponed until {self.due_date}. (Use `vinca last-card postpone 0 to undo).'


        def review(self):
                start = time.time()
                grade_key = self.review_verses() if self.verses else self.review_basic()
                grade = GRADE_DICT.get(grade_key, 'exit')
                stop = time.time()

                elapsed_seconds = int(stop - start)

                self.review_count += 1
                self.reviewing_seconds += elapsed

                self.process_grade(grade, elapsed_seconds)


        def review_basic(self):
                with AlternateScreen():
                        print(self.front_text)
                        ansi.light(); print('\n', self.tags); ansi.reset()
                        print('\n\n\n')
                        with DisplayImage(self.front_image):
                            char = readkey() # press any key to flip the card
                            if char in ['x','a','q']: # immediate exit actions
                                    return char
                        with DisplayImage(self.back_image):
                            print(self.back_text)
                            return readkey()

        def review_verses(self):
                with AlternateScreen():
                        lines = self.front_text.splitlines()
                        print(lines.pop(0)) # print the first line
                        for line in lines:
                                char = readkey() # press any key to continue
                                if char in ['x','a','q']: # immediate exit actions to abort the review
                                        return char
                                print(line)

                        # grade the card
                        return = readkey()

        def edit(self):
                start = time.time()
                self.edit_verses() if self.verses else self.edit_basic()
                stop = time.time()
                elapsed_seconds = int(stop - start)
                self.edit_count += 1
                self.editing_seconds += elapsed


        def edit_basic(self):
                self.front_text = VimEditor(text = self.front_text, prompt = 'Q: ').run()
                self.back_text = VimEditor(text = self.back_text, prompt = 'A: ').run()

        def edit_verses(self):
                self.front_text = VimEditor(text = self.front_text, prompt = 'Verses:\n').run()

