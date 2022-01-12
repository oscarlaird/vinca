
from vinca._lib.terminal import AlternateScreen
from vinca._lib.readkey import readkey
from vinca._lib.video import DisplayImage

def make_string(card):
        f = ' / '.join((card.path / 'front').read_text().splitlines())
        b = ' / '.join((card.path / 'back').read_text().splitlines())
        return f + ' | ' + b

def review(card):
        front_text = card.path / 'front'
        back_text = card.path / 'back'
        front_image = card.path / 'front.png'
        back_image = card.path / 'back.png'

        with AlternateScreen():
                # front text
                print(front_text.read_text())

                with DisplayImage(front_image):

                    char = readkey() # press any key to flip the card
                    print('\n\n\n')
                    if char in ['x','a','q']: # immediate exit actions
                            return char

                with DisplayImage(back_image):

                    # back text
                    print(back_text.read_text())

                    return readkey()
