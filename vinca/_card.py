import subprocess
import json
import datetime
TODAY = datetime.date.today()
DAY = datetime.timedelta(days=1)
from pathlib import Path
from shutil import copyfile

from vinca import _reviewers, _editors
from vinca._lib.vinput import VimEditor
from vinca._lib.random_id import random_id

class Card(dict):
        # Card class can load without 
        default_metadata = {'editor': 'base', 'reviewer':'base',
                            'tags': [], 'deleted': False,
                            'due_date': TODAY,}

        def __init__(self, row, update_callback):
                assert type(row) is dict
                self.update_callback = update_callback
                super().__init__(self, row)

        def __str__(self):
                return self['fronttext'] + self['backtext']

        def __setitem__(self, *args, **kwargs):
                super().__setitem__(self, *args, **kwargs)
                # commit change to card-dictionary to SQL database
                self.update_callback()

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
