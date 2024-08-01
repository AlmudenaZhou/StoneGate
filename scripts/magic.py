import json
import os
import random

from scripts.variables import general_path


class MagicCreation:

    def __init__(self) -> None:
        self.path: str = os.path.join(general_path, 'configurations', 'magic')

    def create_magic(self):

        magic_data, magic_words, done_magic_words = self.get_data()

        magic = Magic(magic_words["words_list"], magic_data, done_magic_words)

        magic.create_words()

        return magic

    # Get data from JSONs
    def get_data(self):

        done_magic_words = dict()

        with open(f'{self.path}/magic_data.json', 'r') as data:
            magic_data = json.load(data)
        
        with open(f'{self.path}/magic_words.json', 'r') as data:
            magic_words = json.load(data)

        try:

            with open(f'{self.path}/done_magic_words.json', 'r') as data:
                done_magic_words = json.load(data)

        except Exception as e:

            print(f'Error: {e}')

        return magic_data, magic_words, done_magic_words

    def generate_random_words(self):
        pass


class Magic:

    def __init__(self, words_list: list = list(), words_data: list = list(), done_words_dict: dict = dict()) -> None:
        
        self.input_done_words_dict = done_words_dict   # Input already made magic words

        self.input_words_list = words_list   # May include branch
        self.input_words_data = words_data    # Include branch, efect, cost and probablity

        self.words = dict()  # Final words

    def create_words(self, modify_cost: bool = False):

        # Add predefined words
        for key in self.input_done_words_dict:
            name, branch, effect, cost, probability = self.input_done_words_dict[key]

            word = WordMagic(name, branch, effect, cost, probability)

            if modify_cost:
                word.modify_cost(round(cost/20))

            self.words[name] = word

        # Create and add new words
        for name in self.input_words_list:
            branch, effect, cost, probability = self.get_random_magic(not_repeated=True)
            word = WordMagic(name, branch, effect, cost, probability)

            if modify_cost:
                word.modify_cost(round(cost/20))

            self.words[name] = word

            if not self.input_words_data:
                print("No more magic avaible")
                break
    
    def get_random_magic(self, not_repeated: bool = True):

        random_magic_index = random.randint(0, len(self.input_words_data)-1)
        key = list(self.input_words_data.keys())[random_magic_index]
        magic = self.input_words_data[key]

        if not_repeated:
            # Delete this magic
            self.input_words_data.pop(key)

        return magic


class WordMagic:

    def __init__(self, name, branch, effect, cost, probability) -> None:
        
        self.name: str = name
        self.branch: str = branch
        self.effect: dict = effect
        self.cost: int = cost
        self.probability: float = probability
        
    def modify_cost(self, random):

        self.cost = self.cost + random.randint(-random, random)

    def modify_name(self, extra):
        pass

    @staticmethod
    def magic_effects(sword, effect_rune):
        effect = effect_rune.effect
        if 'attack' in effect.keys():
            sword.extra_damage += effect['attack']


magic_creation = MagicCreation()

magic_dict = magic_creation.create_magic().words
