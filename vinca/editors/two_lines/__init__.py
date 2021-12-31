from vinca.lib.vinput import VimEditor

def edit(card):
	front_path = (card.path / 'front')
	back_path  = (card.path / 'back')
	front = front_path.read_text()
	back  =  back_path.read_text()

	new_front = VimEditor(text = front, prompt = 'Q: ').run()
	front_path.write_text(new_front)
	
	new_back = VimEditor(text = back, prompt = 'A: ').run()
	back_path.write_text(new_back)

