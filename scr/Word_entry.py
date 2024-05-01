import json
from abc import ABC, abstractmethod

class Word_entry:
    '''
    The class contains two attributes: `headword` (str) and `definition_entries` (list). 
    Each member of `definition_entries` is a python dictionary, whose keys are `part of speech`, `conjugation`, `definition`, `usage`, and `examples`
    '''
    def __init__(self, word:str) -> None:
        self.headword = word
        self.definition_entries = []


class Dictionary_reader(ABC):
    '''
    Given a list `word_list` of words, the class saves the entries for the words in the dictionary.
    '''
    def __init__(self, json_path:str, word_list:list) -> None:
        with open(json_path) as file:
            self.dictionary = json.load(file)
        self.word_list = word_list
        self.word_entry_list = []


    def get_word_entry_list(self):
        self._update_word_entry_list(self.word_list)
        return self.word_entry_list


    @abstractmethod
    def _update_word_entry_list(self, word_list:list) -> None:
        pass

