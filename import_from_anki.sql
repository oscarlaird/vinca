-- instructions for converting an ANKI collection to VINCA
-- only works for 'Basic cards'


-- create a temporary column in cards called anki_card_id
-- ANKI creates a unique id for each card, note, and review
-- by taking the milliseconds since the UNIX epoch
-- I convert this to my special variety of Julian Date (days since 0:00 Nov 24 4774 BC)
-- notes.flds contains all the real content. The fronttext and backtext is divided by an escape character.

-- add the basic notes as cards
insert into test.cards (anki_card_id, create_date, front_text, back_text)
 select * from (select
 cards.id as anki_card_id,
 (julianday(cards.id / 1000, 'unixepoch', 'localtime') + 0.5) as create_date,
 substring(notes.flds,1,instr(notes.flds,'')-1) as front_text,
 substring(notes.flds,instr(notes.flds,'')+1,1000) as back_text
 from cards left join notes on cards.nid=notes.id);

-- now copy over the reviews
insert into test.reviews (card_id, date, seconds, action_grade)
 select * from (select
 test.cards.id as card_id,
 (julianday(revlog.id / 1000, 'unixepoch', 'localtime') + 0.5) as date,
 time/1000 as seconds,
 (case ease when 1 then 'again' when 2 then 'hard' when 3 then 'good' when 4 then 'easy' end) as action_grade
 from revlog left join test.cards on test.cards.anki_card_id=revlog.cid);

-- now delete the column called anki_card_id

