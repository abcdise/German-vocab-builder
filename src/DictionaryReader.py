import json
from copy import deepcopy
from abc import ABC, abstractmethod

pons_json_path = '../../../../../Library/Mobile Documents/com~apple~CloudDocs/Projects/Vocab Builder/German/Dictionary/PONS.json'
refined_pons_json_path = '../../../../../Library/Mobile Documents/com~apple~CloudDocs/Projects/Vocab Builder/German/Dictionary/Refined PONS.json'
phrase_json_path = '../../../../../Library/Mobile Documents/com~apple~CloudDocs/Projects/Vocab Builder/German/Dictionary/Phrase.json'


class WordEntry:
    '''
    The class contains two attributes: `headword` (str) and `definition_entries` (list). 
    Each member of `definition_entries` is a python dictionary, whose keys are `part of speech`, `conjugation`, `definition`, `usage`, and `examples`
    '''
    def __init__(self, word:str) -> None:
        self.headword = word
        self.definition_entries = []


class DictionaryReader(ABC):
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


class GermanDictionaryReader(DictionaryReader):
    def __init__(self, json_path, word_list:list) -> None:
        super().__init__(json_path, word_list)

    def _update_word_entry_list(self, word_list: list) -> None:
        for word in word_list:
            word_entry = WordEntry(word)
            definition_entries = self.dictionary.get(word, [])
            if definition_entries:
                for entry in definition_entries:
                    definition_entry = dict()
                    definition = entry['Definition']
                    examples = entry['Beispiele']
                    forms = entry['Formen']
                    redewendungen = entry['Redewendungen']
                    anwendung = entry['Anwendung']
                    definition_entry['conjugation'] = forms
                    definition_entry['definition'] = definition
                    definition_entry['examples'] = redewendungen + examples
                    definition_entry['part of speech'] = ''
                    definition_entry['usage'] = anwendung
                    word_entry.definition_entries.append(deepcopy(definition_entry))
                
                self.word_entry_list.append(deepcopy(word_entry))
            else:
                print(f'The word {word} does not exist in the json file!')


class PONSReader(GermanDictionaryReader):
    def __init__(self, word_list: list) -> None:
        super().__init__(json_path=refined_pons_json_path, word_list=word_list)


class PhraseReader(GermanDictionaryReader):
    def __init__(self, word_list: list) -> None:
        super().__init__(json_path=phrase_json_path, word_list=word_list)