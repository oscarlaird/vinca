import json
from pathlib import Path

class Config(dict):
        path = Path(__file__).parent / 'config.json'
        home = Path.home()
        default_cards_path = home / 'cards'
        default_config = {"cards_path": str(default_cards_path), "last_card_path": None}
        
        def __init__(self):
                if not self.path.exists():
                        self.path.touch()
                        json.dump(self.default_config, self.path.open('w'))
                dict.__init__(self, self.load())
                if not self.cards_path.exists():
                        self.cards_path.mkdir()
        
        def load(self):
                try:
                        with open(self.path) as f:
                                return json.load(f)
                except json.decoder.JSONDecodeError:
                        print(f'Error decoding json file {self.path}')
                        self.path.unlink() # delete config.json
                        print('File has been deleted. Hopefully this solves the problem.')
                        exit()

        def save(self):
                with open(self.path,'w') as f:
                        json.dump(self, f)

        def set_cards_path(self, path):
                ''' vinca will look for cards in the chosen directory '''
                self['cards_path'] = str(path)
                self.save()

        @property
        def last_card_path(self):
                if self['last_card_path'] is None:
                        return 'no last card available'
                return Path(self['last_card_path'])

        @last_card_path.setter
        def last_card_path(self, card_path):
                self['last_card_path'] = str(card_path)
                self.save()

        @property
        def cards_path(self):
                return Path(self['cards_path'])

config = Config()
