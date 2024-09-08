import json
from pathlib import Path
from copy import deepcopy
import requests
from numpy import random
import csv
import re


class Configurator:
    '''
    A class that manipulates the configuration json file.
    Members:
    json_path: The path of the json file.
    config(dict): The data saved in the config json file.
    '''
    def __init__(self, json_path:str):
        self.json_path = Path(json_path)
        keys = ['all', 'new', 'review', 'last change']
        if Path.exists(self.json_path):
            with open(self.json_path) as file:
                try:
                    self.config = json.load(file)
                except json.JSONDecodeError:
                    print('Failed to load the json file')
                    self.config = dict.fromkeys(keys)
        else:
            self.config = dict.fromkeys(keys)


    def initialise(self, word_list:list):
        '''
        The method create a new configuration dictionary based on the word list inputs and write the dictionary
        to the config file.
        '''
        self.config['all'] = deepcopy(word_list)
        self.config['new'] = deepcopy(word_list)
        self.config['review'] = []
        self.config['last change'] = []
        self.__export()


    def reset(self):
        '''
        The method set the `review` list to an empty list and set the `new` list to the whole list.
        '''
        self.config['new'] = self.config['all']
        self.config['review'] = []
        self.config['last change'] = []
        self.__export()

    
    def get_n_words_to_learn(self, n:int):
        list_to_return = self.config['new'][:n]
        if len(list_to_return) < n:
            print('Congratulations! You have finished studying the list.')
        return list_to_return
    

    def study_n_words(self, n:int):
        new_list = self.config['new']
        review_list = self.config['review']
        new_word_list = self.get_n_words_to_learn(n)
        review_list += new_word_list
        new_list = [word for word in new_list if word not in new_word_list]
        self.config['review'] = deepcopy(review_list)
        self.config['new'] = deepcopy(new_list)
        self.config['last change'] = deepcopy(new_list)
        self.__export()


    def __export(self):
        with open(self.json_path, 'w') as file:
            json.dump(self.config, file, indent=4, ensure_ascii=False)



class AnkiCommunicator:
    def __init__(self):
        self.base_url = 'http://localhost:8765'

    def __get_request(self, action, params):
        return {'action': action, 'params': params, 'version': 6}
    
    def __invoke(self, action, params):
        data = json.dumps(self.__get_request(action, params))
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.base_url, data=data, headers=headers)
        response_json = response.json()
        if 'error' in response_json and response_json['error']:
            raise Exception(f'Failed to fetch card info: {response_json["error"]}')
        return response_json['result']

    def __get_cards_id_in_n_days(self, n):
        query = f'prop:due<={n}'
        response = self.__invoke('findCards', {'query': query})
        return response

    def get_words_in_n_days(self, n, deck_name):
        card_ids = self.__get_cards_id_in_n_days(n)
        if not card_ids:
            return [], dict()
        cards_info = self.__invoke('cardsInfo', {'cards': card_ids})
        result_list = [(self._extract_word_from_field(card['fields']['Front']['value']), self._extract_def_from_field(card['fields']['Back']['value'])) \
                       for card in cards_info if card and card['deckName'] == deck_name]
        result_dict = dict()
        for term_def in result_list:
            result_dict[term_def[0]] = result_dict.get(term_def[0], []) + [term_def[1]]
        return result_dict

    def get_words_for_tomorrow(self, deck_name):
        return self.get_words_in_n_days(1, deck_name)

    def _extract_word_from_field(self, input_string):
        matches = re.findall(r'<b>(.*?)</b>', input_string)
        if matches:
            return matches[0]
        else:
            print(f'There is something wrong in the card: {input_string}')
            return None
        
    def _extract_def_from_field(self, input_string):
        rows = input_string.split('<br><br>')
        # If the length of the rows is greater than 2, then check if the third row contains Chinese characters
        if len(rows) > 2:
            # If the third row contains Chinese characters, then return the second row as the definition
            if re.search(r'[\u4e00-\u9fff]', rows[2]):
                return rows[1]
            else:
                return rows[2]
        else: # If the 
            return rows[1]


class AnkiCardWriter:
    '''
    The writer takes a list of word entries as an input. The user can use the method `write_cards` to create a csv file that are suitable for Anki imports.
    '''
    def __init__(self, word_entry_list: list):
        self.word_entry_list = word_entry_list
        self.Anki_cards = []

    def write_cards(self, csv_path = str, shuffle_cards=True):
        self.__write_cards(self.word_entry_list)
        if shuffle_cards:
            random.shuffle(self.Anki_cards)
        with open(csv_path, 'w', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerows(self.Anki_cards)



    def __write_cards(self, word_entry_list: list):
        '''
        Updates the list `self.Anki_cards`.
        '''
        for word_entry in word_entry_list:
            word = word_entry.headword
            definition_entries = word_entry.definition_entries
            for definition_entry in definition_entries:
                conjugation = definition_entry['conjugation']
                examples = definition_entry['examples']
                definition = definition_entry['definition']
                usage = definition_entry['usage']
                part_of_speech = definition_entry['part of speech']
                anki_card = []
                front = ''
                back = ''
                front += '<b>' + word + '</b>' + '<br>' + '<br>'
                back += (part_of_speech + '<br>' + '<br>') if part_of_speech else ''
                back += (conjugation + '<br>' + '<br>') if conjugation else ''
                back += (usage + '<br>' + '<br>') if usage else ''
                back += definition
                for sentence in examples:
                    front += '<i>' + sentence + '</i>' + '<br>'
                anki_card.append(front)
                anki_card.append(back)
                self.Anki_cards.append(anki_card)

    