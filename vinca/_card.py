import subprocess

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

        fields = ['id', 'fronttext', 'backtext', 'frontimage', 'backimage', 'frontaudio', 'backaudio', 'deleted', 'create_date', 'due_date', 'editing_seconds', 'reviewing_seconds', 'edit_count', 'review_count', 'stability', 'retrievability', 'tag']

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

        def __str__(self):
                return self['fronttext'] + ' | ' + self['backtext']

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
                return self['due_date'] <= date

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
