from vinca._lib.vinput import VimEditor

def edit(card):
        card.front_text = VimEditor(text = card.front_text, prompt = 'Q: ').run()
        card.back_text = VimEditor(text = card.back_text, prompt = 'A: ').run()

