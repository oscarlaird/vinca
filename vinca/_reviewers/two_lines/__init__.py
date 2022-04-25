
from vinca._lib.terminal import AlternateScreen
from vinca._lib.readkey import readkey
from vinca._lib.video import DisplayImage
from vinca._lib import ansi

def review(card):

        with AlternateScreen():
                # front text
                print(card.front_text)
                ansi.light()
                print('\n',card.tags)
                ansi.reset()

                with DisplayImage(card.front_image):

                    char = readkey() # press any key to flip the card
                    print('\n\n\n')
                    if char in ['x','a','q']: # immediate exit actions
                            return char

                with DisplayImage(card.back_image):

                    # back text
                    print(card.back_text)

                    return readkey()
