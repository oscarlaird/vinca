from pathlib import Path
import sqlite3

class Database:
        def __init__(self, path):
                self.path = Path(path) # I would probably want Python FIRE to automatically cast paths
                self.conn = sqlite3.connect(self.path)
                self.conn.row_factory = sqlite3.Row #return entries as dictionaries not tuples
                self.cursor = self.conn.cursor()

        def update_card(self, card):
                self.cursor.execute(f'SELECT * FROM cards WHERE id = {card.id}')
                old_row = dict(self.cursor.fetchone())
                new_row = card
                assert old_row['id'] == new_row['id']
                id = old_row['id']
                for key, new_value in new_row.items():
                    old_value = old_row[key]
                    if old_value != new_value:
                        self.cursor.execute(f'UPDATE cards SET {key} = {new_value} WHERE id = {id}')
                conn.commit()

        def create_card(self, card):
                ''' returns the id of a new card added to the table '''
                raise NotImplementedError
                pass

        def load_card(self, card):
                ''' reads the table for given id and returns row as a dictionary '''
                self.cursor.execute(f'SELECT * FROM cards WHERE id = {card.id}')
                return dict(cursor.fetchone())
