from vinca.card import Card

def two_lines():
	''' make a simple question and answer card '''
	new_card = Card(create=True)
	new_card.editor, new_card.reviewer, new_card.scheduler = 'two_lines', 'two_lines', 'base'
	(new_card.path / 'front').touch()
	(new_card.path / 'back').touch()
	new_card.edit()
	return new_card
