""" script for exporting George's old vinca cards to SQL """
import ovinca  # old vinca
import vinca._cli_objects as vinca
from vinca._card import Card
import sqlite3
curs = sqlite3.connect(':memory:').cursor()

for oc in ovinca.collection[1714:]:
    # instantiate new card
    nc = Card._new_card(vinca.col._cursor)
    print(nc.id)
    # set create_date
    timestamp = str(oc.create_date) + ' 00:00:00'
    julian_create_date = curs.execute('SELECT julianday(?, "localtime") + 0.5', (timestamp,)).fetchone()[0]
    nc.create_date = julian_create_date
    # copy text fields
    if '|' in oc.string:
        nc.front_text, nc.back_text = oc.string.replace(' \ ','\n').split(' | ',maxsplit=1)
    else:
        nc.front_text = oc.string.replace(' \ ','\n')
        nc.verses = True
    image_path = oc.path / 'back.png'
    if image_path.exists():
            nc.back_image = image_path.read_bytes()
    # set tags
    nc.tag(*oc.tags)
    # copy over review history
    for h in oc.history:
            juliandate = curs.execute('SELECT julianday(?, "localtime") + 0.5', (str(h.date) + ' 00:00:00',)).fetchone()[0]
            vinca.col._cursor.execute('INSERT INTO reviews (date, seconds, action_grade, card_id) VALUES (?, ?, ?, ?)', (juliandate, h.time, h.grade, nc.id))
            vinca.col._cursor.connection.commit()
    # schedule according to new system
    nc._schedule()

