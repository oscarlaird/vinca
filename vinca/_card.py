import time
from pathlib import Path

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from rich import print

from vinca._lib.terminal import AlternateScreen
from vinca._lib.readkey import readkey
from vinca._lib.video import DisplayImage
from vinca._lib import ansi
from vinca._lib.julianday import JulianDate, today

from vinca._scheduling import Review, History

TODAY = today()  # int representing day

GRADE_DICT = {'1': 'again',
              '2': 'hard',
              '3': 'good', ' ': 'good', '\r': 'good', '\n': 'good',
              '4': 'easy'}
STUDY_ACTION_GRADES = ('again', 'hard', 'good', 'easy')
BUREAU_ACTION_GRADES = ('edit', 'exit', 'preview')



class Card:
    # A card is a dictionary
    # its data is loaded from SQL on the fly and saved to SQL on the fly

    _misc_fields = ('card_type','visibility')
    _date_fields = ('create_date', 'due_date')
    _text_fields = ('front_text', 'back_text')
    _media_id_fields = ('front_image_id', 'back_image_id', 'front_audio_id', 'back_audio_id')
    _virtual_media_fields = ('front_image','back_image','front_audio','back_audio')
    _media_fields = _text_fields + _virtual_media_fields
    _fields = ('id',) + _misc_fields + _date_fields + _media_fields + _media_id_fields

    # let us access key-val pairs from the dictionary as simple attributes
    # these in turn reference the more complex __getitem__ and __setitem__ methods
    for _f in _fields:
        exec(
            f'''
@property
def {_f}(self):
        return self["{_f}"]
@{_f}.setter
def {_f}(self, new_value):
        self["{_f}"] = new_value
'''
        )


    @property
    def help_string(self):
        s =  '[dim]'
        s += '(Q)uit    (E)dit    (T)ag    (D)elete  \n\n'
        for i, grade in enumerate(('again','hard','good','easy'),start=1):
            hypo_due = JulianDate(self.history.hypothetical_due_date(grade))
            s += f'({i}) {grade:8s}+{hypo_due.relative_date} days from today\n'
        return s


    def __init__(self, id, cursor):
        self._cursor = cursor
        self._dict = dict(id=id)
        self._hotkeys = {'e': self.edit,
                         't': self.edit_tags,
                         'd': self._toggle_delete,
                         '+': self.postpone, }

    def __str__(self):
        s = ''
        if self.visibility=='deleted':
            s += ansi.codes['red']
        elif self.is_due:
            s += ansi.codes['blue']
        s += self.front_text.replace('\n', ' / ')
        s += ' | '
        s += self.back_text.replace('\n', ' / ')
        s += ansi.codes['reset']
        return s

    def metadata(self):
        metadata = {field: str(getattr(self, field)) for field in self._fields}
        return metadata

    @staticmethod
    def _is_path(arg):
        """ Check if an argument specifies a file """
        if not arg or type(arg) not in (str, Path):
            return
        try:
            return Path(arg).exists()
        except:
            return

    # commit to SQL any variables that are changed (by editing, deleting, scheduling, etc.)
    def __setitem__(self, key, value):
        assert key != 'id', 'Card Id cannot be changed!'
        assert key in self._fields
        self._dict[key] = value
        # commit change to card-dictionary to SQL database
        if key in self._virtual_media_fields:
            self._cursor.execute('INSERT INTO media (content) VALUES (?);',(value,))
            self._cursor.execute('SELECT id FROM media WHERE rowid = last_insert_rowid()')
            media_id = self._cursor.fetchone()[0]
            id_key = key + '_id' # change front_image to front_image_id
            self._cursor.execute(f'INSERT INTO edits (card_id, {id_key}) VALUES (?, ?)', (self.id, media_id))
        else:
            self._cursor.execute(f'INSERT INTO edits (card_id, {key}) VALUES (?, ?)',(self.id, value))
        self._cursor.connection.commit()

    # access __setitem__ functionality from the command line
    # allows for setting media or text field with a filepath
    def set(self, key, value):
        'set the text or image for a card: `set front_image ./diagram.png`'
        # if a filename is specified as the value read the contents of that file.
        if key in self._media_fields and self._is_path(value):
            if key in self._text_fields:
                value = Path(value).read_text()
            if key in self._virtual_media_fields:
                value = Path(value).read_bytes()
        self.__setitem__(key, value)

    # load attributes from SQL on the fly
    # and put them in self._dict for future reference
    def __getitem__(self, key):
        if key not in self._fields:
            raise KeyError(f'Field "{key}" does not exist')
        if key not in self._dict.keys():
            # load attribute from the database if we haven't yet
            # for the special virtual field front_image
            # we have to look up the content in the media table based on front_image_id
            if key in self._virtual_media_fields:
                key_id = key + '_id' # change front_image to front_image_id
                media_id = self._cursor.execute(f'SELECT {key_id} FROM cards WHERE id = ?',(self.id,)).fetchone()[0]
                value = None if not media_id else self._cursor.execute(f'SELECT content FROM media '
                                                    'WHERE id = ?', (media_id,)).fetchone()[0]
            # other keys we can query from the cards table directly
            else:
                value = self._cursor.execute(f'SELECT {key} FROM cards'
                                             ' WHERE id = ?', (self.id,)).fetchone()[0]
            # preprocess certain values to cast them to better types:
            if key in self._text_fields:
                # if SQL passes us an Integer or None
                # this is going to cause errors
                value = str(value or '')
            # A JulianDate is just a wrapper class for floats
            # which prints out as a date
            if key in self._date_fields:
                value = JulianDate(value)
            self._dict[key] = value
        return self._dict[key]

    def __len__(self):
        # Fire sees __getitem__ and thinks we can be indexed
        # by defining len=0 we tell it not to try to index us
        return 0

    def delete(self):
        self.visibility = 'deleted';
        return 'to undo use the restore command'

    def _toggle_delete(self):
        if self.visibility == 'purged':
            return
        #raise BaseException(self.visibility=='deleted', self.visibility, 'deleted')
        self.visibility = 'visible' if self.visibility=='deleted' else 'deleted'

    def restore(self):
        self.visibility = 'visible'
        return 'card restored'

    @property
    def is_due(self):
        return self.due_date <= TODAY

    def postpone(self, n=1):
        # 'Make card due n days after today. (default 1)'
        tomorrow = TODAY + n
        hour = self.due_date % 1
        self.due_date = tomorrow + hour
        return f'Postponed until {self.due_date}.'

    def review(self):
        start = time.time()
        grade_key = self._review_verses() if self.card_type=='verses' else self._review_basic()
        stop = time.time()
        elapsed_seconds = int(stop - start)

        if grade_key in ('d','\x1b[P'): # 'd' or 'Delete' keys
                self.visibility = 'deleted'
        if grade := GRADE_DICT.get(grade_key):
                self._log(grade=grade, seconds=elapsed_seconds)
                self._schedule()
        return grade_key

    def _review_basic(self):
        # review the card and return the keystroke pressed by the user

        def edit_then_review():
            ansi.move_to_top();
            ansi.clear_to_end()
            self.edit()
            return self._review_basic()

        with AlternateScreen():
            print(f'[bold]{self.front_text}')
            print('\n', f'[dim yellow italic]{" ".join(self.tags)}', '\n', sep='')
            with DisplayImage(data_bytes=self.front_image):
                char = readkey()  # press any key to flip the card
                if char == 'e':  # edit the card and then review it
                    return edit_then_review()
                if char == 't':
                    self.edit_tags()
                if char in ('d', '\x1b[P', 'q', '\x1b'): # immediate exit actions
                    return char
            with DisplayImage(data_bytes=self.back_image):
                print(f'[bold]{self.back_text}')
                print('\n\n')
                print(self.help_string)
                char = readkey()
                if char == 'e':
                    return edit_then_review()
                if char == 't':
                    self.edit_tags()
                return char

    def _review_verses(self):
        def edit_then_review():
            ansi.move_to_top();
            ansi.clear_to_end()
            self.edit()
            return self._review_verses()

        with AlternateScreen():
            print('Recite the lines one by one. Press space to show the next line.')
            print(f'[dim yellow italic]{" ".join(self.tags)}', '\n', sep='')
            lines = self.front_text.splitlines()
            print(f'[bold]{lines.pop(0)}')
            for line in lines:
                char = readkey()  # press any key to continue
                if char == 'e':  # edit the card and then review it
                    return edit_then_review()
                if char == 't':
                    self.edit_tags()
                if char in ('d', '\x1b[P', 'q', '\x1b'): # immediate exit actions
                    return char
                print(f'[bold]{line}')

            # grade the card
            print('\n\n')
            print(self.help_string)
            char = readkey()
            if char == 'e':
                return edit_then_review()
            if char == 't':
                self.edit_tags()
            return char

    def edit(self):
        start = time.time()
        self._edit_verses() if self.card_type=='verses' else self._edit_basic()
        stop = time.time()
        elapsed_seconds = int(stop - start)
        self._log('edit', elapsed_seconds)

    def _edit_basic(self):
        self.front_text = prompt('Question:   ',
                                 default=self.front_text,
                                 multiline=True, vi_mode=True,
                                 bottom_toolbar=lambda: 'press ESC-Enter to confirm')
        self.back_text = prompt('Answer:     ',
                                default=self.back_text,
                                multiline=True, vi_mode=True,
                                bottom_toolbar=lambda: 'press ESC-Enter to confirm')

    def _edit_verses(self):
        self.front_text = prompt('Verses:     ',
                                 default=self.front_text,
                                 multiline=True, vi_mode=True,
                                 bottom_toolbar=lambda: 'press ESC-Enter to confirm')

    def _log(self, grade, seconds):
        self._cursor.execute('INSERT INTO reviews (card_id, seconds, grade)'
                             ' VALUES (?, ?, ?)', (self.id, seconds, grade))
        self._cursor.connection.commit()

    @property
    def history(self):
        self._cursor.execute('SELECT date, grade, seconds FROM reviews WHERE card_id = ?',(self.id,))
        reviews = [Review(*row) for row in self._cursor.fetchall()]
        return History(reviews)

    def _schedule(self):
        self.due_date = self.history.new_due_date

    @property
    def tags(self):
        # raise ValueError(str(self.id))
        tags = self._cursor.execute('SELECT tag FROM tags'
                                    ' WHERE card_id = ?', (self.id,)).fetchall()
        tags = [row[0] for row in tags]
        return tags

    def _remove_tag(self, tag):
        self._cursor.execute('INSERT INTO tag_edits'
                             ' (card_id, tag, applied) VALUES (?, ?, ?)', (self.id, tag, False))
        self._cursor.connection.commit()

    def _add_tag(self, tag):
        if tag not in self.tags:
            self._cursor.execute('INSERT INTO tag_edits'
                                 ' (card_id, tag) VALUES (?, ?)', (self.id, tag))
            self._cursor.connection.commit()

    def edit_tags(self):
        new_tags = prompt('tags: ',
                          default=' '.join(self.tags),
                          completer=WordCompleter(self._collection_tags()),
                          ).split()
        for tag in self.tags:
            self._remove_tag(tag)
        for tag in new_tags:
            self._add_tag(tag)

    def _collection_tags(self):
        self._cursor.execute('SELECT tag FROM tags GROUP BY tag')
        tags = [row[0] for row in self._cursor.fetchall()]
        return tags

    def tag(self, *tags):
        """ add tags to the card """
        for tag in tags:
            self._add_tag(tag)

    @classmethod
    def _new_card(cls, cursor):
        cursor.execute("INSERT INTO edits DEFAULT VALUES")
        cursor.connection.commit()
        id = cursor.execute("SELECT card_id FROM edits WHERE"
                            " rowid = last_insert_rowid()").fetchone()[0]
        return cls(id, cursor)
