from vinca.card import Card

def verses():
	''' make a card which quizzes one line at a time\nfor poetry, oratory, recipes '''
	new_card = Card(create=True)
	new_card.editor, new_card.reviewer, new_card.scheduler = 'verses', 'verses', 'base'
	new_card.edit()
	return new_card
