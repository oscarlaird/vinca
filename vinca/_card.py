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
RESET_ACTION_GRADES = ('create', 'again')
STUDY_ACTION_GRADES = ('hard', 'good', 'easy')
BUREAU_ACTION_GRADES = ('edit', 'delete', 'exit', 'preview')

import time
from pathlib import Path

from vinca._lib.julianday import today
TODAY = today() # int representing day

class Card:
        # A card is a dictionary
        # its data is loaded from SQL on the fly and saved to SQL on the fly

        _fields = ('id', 'front_text', 'back_text', 'front_image', 'back_image', 'front_audio', 'back_audio', 'verses', 'deleted', 'create_date', 'due_date',)
        _date_fields = ('create_date','due_date')

        # let us access key-val pairs from the dictionary as simple attributes
        for f in _fields:
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
        del f



        def __init__(self, id, cursor):
                self._cursor = cursor
                self._dict = dict(id = id)
                self._hotkeys = {'e': self.edit,
                                 't': self.edit_tags,
                                 'd': self._toggle_delete,
                                 '+': self.postpone,}

        def __str__(self):
                s = ''
                if self.deleted:
                        s += ansi.codes['red']
                elif self.is_due:
                        s += ansi.codes['blue']
                s += self.front_text + ' | ' + self.back_text
                s += ansi.codes['reset']
                return s

        def metadata(self):
                return {field:getattr(self,field) for field in self._fields +
                        ('interval','ease','last_study_date','last_reset_date','tags')}

        def __setitem__(self, key, value):
                assert key != 'id', 'Card Id cannot be changed!'
                assert key in self._fields
                self._dict[key] = value
                # commit change to card-dictionary to SQL database
                self._cursor.execute(f'UPDATE cards SET {key} = ? WHERE id = ?', (value, self.id))
                self._cursor.connection.commit()
        set = __setitem__

        def __getitem__(self, key):
                if key not in self._fields:
                        raise KeyError(f'Field "{key}" does not exist')
                if key not in self._dict.keys():
                        # load attribute from the database if we haven't yet
                        value = self._cursor.execute(f'SELECT {key} FROM cards'
                            ' WHERE id = ?', (self.id,)).fetchone()[0]
                        self[key] = value
                return self._dict[key]

        def __len__(self):
                # TODO Fire sees __getitem__ and thinks we can be indexed
                # by defining len=0 we tell it not to try to index us
                return 0

        def delete(self): 
                self.deleted = True
                return 'Card has been deleted. Use `vinca last-card restore` to undo.'

        def _toggle_delete(self):
                self.deleted = not self.deleted

        def restore(self):
                self.deleted = False
                return 'Card restored.'

        @property
        def is_due(self):
                return self.due_date <= TODAY

        def postpone(self, n=1):
                # 'Make card due n days after today. (default 1)'
                tomorrow = TODAY + n
                hour = self.due_date % 1
                self.due_date = tomorrow + hour
                return f'Postponed until {self.due_date}. (Use `vinca last-card postpone 0 to undo).'


        def review(self):
                start = time.time()
                grade_key = self._review_verses() if self.verses else self._review_basic()
                grade = GRADE_DICT.get(grade_key, 'exit')
                stop = time.time()

                elapsed_seconds = int(stop - start)

                self._log(grade, elapsed_seconds)
                self._schedule()


        def _review_basic(self):
                with AlternateScreen():
                        print(self.front_text)
                        ansi.light(); print('\n', self.tags); ansi.reset()
                        print('\n\n\n')
                        with DisplayImage(data_bytes=self.front_image):
                            char = readkey() # press any key to flip the card
                            if char in ['x','a','q']: # immediate exit actions
                                    return char
                        with DisplayImage(data_bytes=self.back_image):
                            print(self.back_text)
                            return readkey()

        def _review_verses(self):
                with AlternateScreen():
                        lines = self.front_text.splitlines()
                        print(lines.pop(0)) # print the first line
                        for line in lines:
                                char = readkey() # press any key to continue
                                if char in ['x','a','q']: # immediate exit actions to abort the review
                                        return char
                                print(line)

                        # grade the card
                        return readkey()

        def edit(self):
                start = time.time()
                self._edit_verses() if self.verses else self._edit_basic()
                stop = time.time()
                elapsed_seconds = int(stop - start)
                self._log('edit', elapsed_seconds)


        def _edit_basic(self):
                self.front_text = VimEditor(text = self.front_text, prompt = 'Q: ').run()
                self.back_text = VimEditor(text = self.back_text, prompt = 'A: ').run()

        def _edit_verses(self):
                self.front_text = VimEditor(text = self.front_text, prompt = 'Verses:\n').run()


        def _log(self, action_grade, seconds):
                self._cursor.execute('INSERT INTO reviews (card_id, seconds, action_grade)'
                        ' VALUES (?, ?, ?)', (self.id, seconds, action_grade))
                self._cursor.connection.commit()
                    

        @property
        def last_action_grade(self):
                return self._cursor.execute('SELECT action_grade, max(date)'
                        ' FROM reviews WHERE card_id = ?',(self.id,)).fetchone()[0]

        @property
        def last_reset_date(self):
                date = self._cursor.execute('SELECT max(date)'
                        ' FROM reviews WHERE action_grade IN (?, ?) AND card_id = ?',
                        RESET_ACTION_GRADES + (self.id,)).fetchone()[0]
                if date is None:
                        return self.create_date
                return JulianDay(date)

        @property
        def last_study_date(self):
                date = self._cursor.execute('SELECT max(date)'
                        ' FROM reviews WHERE action_grade IN (?, ?, ?, ?, ?) AND card_id = ?',
                        RESET_ACTION_GRADES + STUDY_ACTION_GRADES + (self.id,)).fetchone()[0]
                if date is None:
                        return self.create_date
                return date

        @property
        def ease(self):
                # the ease is the ratio of the card's age to the next interval
                # if ease=1 the intervals will double
                # we calculate ease as an average of our grades
                # consistently grading 'good' yields ease=1
                grades_since_reset = [grade[0] for grade in \
                        list(self._cursor.execute('SELECT action_grade FROM reviews'
                        ' WHERE card_id = ? AND date > ?'
                        ' AND action_grade IN (?, ?, ?)',
                        (self.id, self.last_reset_date) + STUDY_ACTION_GRADES).fetchall())
                        ]
                grade_ease_dict = {'hard': 0, 'good': 1, 'easy': 2}
                e = [grade_ease_dict[grade] for grade in grades_since_reset]
                if not e:
                    return 1
                return sum(e)/len(e)

        @property
        def interval(self):
                # The interval for the next review is calculated from two values:
                # ✠ The Ease
                # ✠ The number of days between the card's creation (or reset) and the most recent study review
                #   This is called "study maturity"
                study_maturity = int(self.last_study_date) - int(self.last_reset_date)
                interval = int(self.ease * study_maturity)
                return max(1, interval)


        def _calc_due_date(self):
                if self.last_action_grade in RESET_ACTION_GRADES:
                        return self.last_reset_date
                return self.last_study_date + self.interval
                
        def _schedule(self):
                self.due_date = self._calc_due_date()

        @property
        def tags(self):
                # raise ValueError(str(self.id))
                tags = self._cursor.execute('SELECT tag FROM tags'
                    ' WHERE card_id = ?', (self.id,)).fetchall()
                tags = [row[0] for row in tags]
                return tags

        def _remove_tag(self, tag):
                tags = self._cursor.execute('DELETE FROM tags'
                    ' WHERE card_id = ? AND tag = ?', (self.id, tag))
                self._cursor.connection.commit()

        def _add_tag(self, tag):
                if tag not in self.tags:
                        tags = self._cursor.execute('INSERT INTO tags'
                            ' (card_id, tag) VALUES (?, ?)', (self.id, tag))
                        self._cursor.connection.commit()

        def edit_tags(self):
                new_tags = VimEditor(prompt = 'tags: ', text = ' '.join(self.tags),
                        completions = self._collection_tags()).run().split()
                for tag in self.tags:
                    self._remove_tag(tag)
                for tag in new_tags:
                    self._add_tag(tag)

        def _collection_tags(self):
                self._cursor.execute('SELECT tag FROM tags GROUP BY tag')
                tags = [row[0] for row in self._cursor.fetchall()]
                return tags

        def tag(self, *tags):
                ' Add tags to a card from the command line '
                for tag in tags:
                        self._add_tag(tag)

        def set_front_image(self, image_png):
                image_path = Path(image_png)
                assert image_path.exists(), f"The image path {image_png} does not exist!"
                self.front_image = image_path.read_bytes()

        def set_back_image(self, image_png):
                image_path = Path(image_png)
                assert image_path.exists(), f"The image path {image_png} does not exist!"
                self.back_image = image_path.read_bytes()
