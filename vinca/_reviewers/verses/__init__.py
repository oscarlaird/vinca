from vinca._lib.terminal import AlternateScreen
from vinca._lib.readkey import readkey

def review(card):

        with AlternateScreen():

                lines = card.front_text.splitlines()
                print(lines.pop(0)) # print the first line
                for line in lines:
                        char = readkey() # press any key to continue
                        if char in ['x','a','q']: # immediate exit actions to abort the review
                                return char
                        print(line)

                # grade the card
                char = readkey()
        
        return char
