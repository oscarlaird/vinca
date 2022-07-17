import time
from pathlib import Path

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from rich import print

from vinca_CLI._lib.terminal import AlternateScreen
from vinca_CLI._lib.readkey import readkey
from vinca_CLI._lib.video import DisplayImage
from vinca_CLI._lib import ansi

from vinca_core.card import Card

GRADE_DICT = {'1': 'again',
              '2': 'hard',
              '3': 'good', ' ': 'good', '\r': 'good', '\n': 'good',
              '4': 'easy'}

class CLI_Card(Card):

    @property
    def help_string(self):
        s =  '[dim]'
        s += '(Q)uit    (E)dit    (T)ag    (D)elete  \n\n'
        for i, (grade, hypo_due_date) in enumerate(self.hypo_due_dates().items(),start=1):
            s += f'({i}) {grade:8s}+{hypo_due_date} days from today\n'
        return s

    @property
    def _hotkeys(self):
        return {'e': self.edit,
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

    # access __setitem__ functionality from the command line
    # allows for setting media or text field with a filepath
    def set(self, key, value):
        'set the text or image for a card: `set front_image ./diagram.png`'
        # if a filename is specified as the value read the contents of that file.
        if key in self._text_fields and self._is_path(value):
            value = Path(value).read_text()
        if key in self._virtual_media_fields and self._is_path(value):
            value = Path(value).read_bytes()
        self.__setitem__(key, value)

     # Python Fire sees __getitem__ and thinks we can be indexed
     # by defining len=0 we tell it not to try to index us
    __len__ = lambda self: 0

    def delete(self):
        self.visibility = 'deleted';
        return 'to undo use the restore command'

    def _toggle_delete(self):
        if self.visibility == 'purged':
            return
        self.visibility = 'visible' if self.visibility=='deleted' else 'deleted'

    def restore(self):
        self.visibility = 'visible'
        return 'card restored'

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
            print('\n', f'[dim yellow italic]{self.tags}', '\n', sep='')
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
            print(f'[dim yellow italic]{self.tags}', '\n', sep='')
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
        self._edit_verses() if self.card_type=='verses' else self._edit_basic()

    def _edit_basic(self):
        start = time.time()
        front_text = prompt('Question:   ',
                             default=self.front_text,
                             multiline=True, vi_mode=True,
                             bottom_toolbar=lambda: 'press ESC-Enter to confirm')
        back_text = prompt('Answer:     ',
                            default=self.back_text,
                            multiline=True, vi_mode=True,
                            bottom_toolbar=lambda: 'press ESC-Enter to confirm')
        elapsed = min(120, time.time() - start)
        self._update({'front_text': front_text, 'back_text': back_text}, seconds=elapsed)

    def _edit_verses(self):
        start = time.time()
        self.front_text = prompt('Verses:     ',
                                 default=self.front_text,
                                 multiline=True, vi_mode=True,
                                 bottom_toolbar=lambda: 'press ESC-Enter to confirm')
        elapsed = min(120, time.time() - start)
        self._update({'front_text': front_text}, seconds=elapsed)


    def edit_tags(self, new_tags=None):
            self.tags = prompt('tags: ',
                              default=self.tags,
                              completer=WordCompleter(self._collection_tags()),
                              )
