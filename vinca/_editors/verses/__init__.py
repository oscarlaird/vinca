# verses editor for lyrics, poetry, oratory, etc.
import subprocess

def edit(card):
	subprocess.run(['vim', card.path/'lines'])
