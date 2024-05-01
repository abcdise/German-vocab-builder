import requests
import pyperclip
from copy import deepcopy
from bs4 import BeautifulSoup
import time
import unicodedata
from pathlib import Path
import json
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path='vars/.env')
api_key = os.getenv('PONS_API_KEY')


class PONS_entry:
    def __init__(self, word:str) -> None:
        self.word = word
        self.raw_entry = dict()
        self.dictionary = dict()
        print(f'Looking up the word {self.word}...')


    def look_up(self, api_key=api_key):
        time.sleep(3)
        self.__get_raw_entry(api_key=api_key)
        self.__parse_headword()
        return self.dictionary
    
    def __get_raw_entry(self, api_key) -> None:
        url = "https://api.pons.com/v1/dictionary"
        headers = {"X-Secret": api_key}
        params = {"q": self.word, "l": 'dede'}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            self.raw_entry = response.json()
        else:
            print(f'\t Failed to look up the word {self.word} from the PONS API.')


    def __parse_line(self, line:str, need_definition:bool, need_grammar:bool):
        # print(line)
        line_soup = BeautifulSoup(line, 'html.parser')
        definition = ''
        grammar = ''
        example_text = ''
        idiom_text = ''
        if need_definition:
            definition_tag = line_soup.find(class_='definition')
            if definition_tag is not None:
                definition = definition_tag.text
                definition = definition.replace('(', '').replace(')', '')
            else:
                definition_tag = line_soup.find(class_='sense')
                if definition_tag is not None:
                    definition = definition_tag.text
                    definition = definition.replace('(', '').replace(')', '')

        if need_grammar:
            grammar_tag = line_soup.find(class_='grammatical_construction')
            if grammar_tag is not None:
                grammar = grammar_tag.text
                if '■' in grammar:
                    grammar = ''
                grammar = grammar.replace('(', '').replace(')', '')
        

        idiom_tag = line_soup.find(class_='idiom_proverb')
        if idiom_tag is not None:
            idiom_text = idiom_tag.text
            if '■' in idiom_text:
                idiom_text = ''
            idiom_text = idiom_text.replace('(', '').replace(')', '')
            # else:
            #     grammar_tag = line_soup.find(class_='idiom_proverb')
            #     if grammar_tag is not None:
            #         grammar = grammar_tag.text
            #     if '■' in grammar:
            #         grammar = ''
            #     grammar = grammar.replace('(', '').replace(')', '')

        example_tag = line_soup.find(class_='example')
        if example_tag is not None:
            example_text = example_tag.text
        
        return definition, grammar, example_text, idiom_text


    def __parse_headword(self) -> None:
        '''
        The function returns the value for the keyword.
        '''

        if not self.raw_entry:
            print(f'\t The data for the word {self.word} has not been fetched.')
        else:
            number_of_hits = len(self.raw_entry[0]['hits'])
            # Each element in `definition_items` is a dictionary, whose keys are "Konjugation", "Definition", "Anwendung", and "Beispiele".
            definition_items = []
            for hit_idx in range(number_of_hits):
                conjugation_text = ''
                headword = self.raw_entry[0]['hits'][hit_idx].get('roms', [])
                if headword:
                    # Get conjugations
                    headword_term_tmp = headword[0].get('headword', '')
                    if headword_term_tmp:
                        headword_term = self.__remove_specific_diacritics_and_dots(headword_term_tmp)
                        if headword_term == self.word:
                            headword_full = headword[0]['headword_full']
                            conjugation_soup = BeautifulSoup(headword_full, 'html.parser')
                            conjugation_tag = conjugation_soup.find(class_='flexion')
                            gender_tag = conjugation_soup.find(class_='genus')
                            if conjugation_tag is not None:
                                conjugation_text = conjugation_tag.text
                                conjugation_text = conjugation_text.replace('<', '').replace('>', '')
                                if gender_tag is not None:
                                    gender = gender_tag.text
                                    conjugation_text = gender + ', ' + conjugation_text

                            # Get definitions
                            num_of_definition_categories = len(headword)
                            for k in range(num_of_definition_categories):
                                num_of_definitions = len(headword[k]['arabs'])
                                for i in range(num_of_definitions):
                                    definition_text = ''
                                    grammar_text = ''
                                    definition_item = dict.fromkeys(['Formen', 'Definition', 'Anwendung', 'Redewendungen', 'Beispiele'])
                                    number_of_lines = len(headword[k]['arabs'][i]['translations'])
                                    grammar_found = False
                                    definition_found = False
                                    examples = []
                                    idioms = []

                                    for j in range(number_of_lines):                                
                                        line = headword[k]['arabs'][i]['translations'][j]['source']
                                        definition_text_tmp, grammar_text_tmp, example_text, idiom_text = self.__parse_line(line=line,
                                                                                                        need_definition=(not definition_found),
                                                                                                        need_grammar=(not grammar_found)
                                                                                                        )
                                        if definition_text_tmp:
                                            definition_text = definition_text_tmp
                                            definition_found = True
                                        if grammar_text_tmp:
                                            grammar_text = grammar_text_tmp
                                            grammar_found = True
                                        if example_text:
                                            examples.append(example_text)
                                        if idiom_text:
                                            idioms.append(idiom_text)

                                    definition_item['Beispiele'] = deepcopy(examples)
                                    definition_item['Redewendungen'] = deepcopy(idioms)
                                    definition_item['Formen'] = conjugation_text
                                    definition_item['Anwendung'] = grammar_text
                                    definition_item['Definition'] = definition_text
                                    if not definition_text:
                                        print(f'The word {self.word} does not a value in the field "Definition".')
                                    
                                    definition_items.append(deepcopy(definition_item))
                            
                            # word_entry.append(definition_items)
                            self.dictionary[self.word] = deepcopy(definition_items)


    def __remove_specific_diacritics_and_dots(self, input_str):
        # Normalize the string to decompose characters into base characters and diacritics
        decomposed_str = unicodedata.normalize('NFD', input_str)
        # Rebuild the string, removing specific diacritics (e.g., the dot below) and middle dots
        # Keep base characters and diacritics like the umlaut
        rebuilt_str = ''.join(
            char for char in decomposed_str
            if unicodedata.category(char) != 'Mn' or unicodedata.name(char).startswith('COMBINING DIAERESIS')
        ).replace('·', '')
        # Normalize again in case the removal of diacritics led to decomposable sequences
        final_str = unicodedata.normalize('NFC', rebuilt_str)
        return final_str
    

class PONS:
    def look_up(self, search_word:str):
        entry = PONS_entry(word=search_word)
        return entry.look_up()


class PONS_writer:
    def __init__(self, dictionary, dictionary_path:str='Dictionary/PONS.json') -> None:
        self.dictionary_json = Path(dictionary_path)
        self.dictionary = dictionary
        if not self.dictionary_json.exists():
            with open(self.dictionary_json, 'w') as json_file:
                json.dump({}, json_file)
        with open(self.dictionary_json) as json_file:
            self.dic = json.load(json_file)
        self.new_entries = dict()

    
    def look_up(self, word_list: list):
        self.new_entries = dict()
        for word in word_list:
            if word not in self.dic.keys():
                entry = self.dictionary.look_up(word)
                entry_detail = entry.get(word, [])
                if entry_detail:
                    self.new_entries[word] = entry.look_up()[word]
                self.__refresh_dictionary()

    
    def __refresh_dictionary(self):
        self.dic.update(self.new_entries)
        with open(self.dictionary_json, 'w') as json_file:
            json.dump(self.dic, json_file, indent=4, ensure_ascii=False)


class PONS_refiner:
    def __init__(self, original_dictionary_path: str, refined_dictionary_path:str):
        self.original_dictionary_json = Path(original_dictionary_path)
        self.refined_dictionary_json = Path(refined_dictionary_path)
        if not self.original_dictionary_json.exists():
            with open(self.original_dictionary_json, 'w') as json_file:
                json.dump({}, json_file)
        if not self.refined_dictionary_json.exists():
            with open(self.refined_dictionary_json, 'w') as json_file:
                json.dump({}, json_file)
        with open(self.original_dictionary_json) as json_file:
            self.original_dict = json.load(json_file)
        with open(self.refined_dictionary_json) as json_file:
            self.refined_dict = json.load(json_file)

    
    def abridge_dict_eg(self, word_list:list):
        return self.__abridge_dict_eg(self.original_dict, word_list)    


    def abridge_dict_def(self, input_dict:dict, word_list:list):
        return self.__abridge_dict_def(input_dict, word_list)
    

    def generate_def_prompt(self, word_list:list, temp_dict:dict):
        dict_str = json.dumps(self.abridge_dict_def(temp_dict, word_list), ensure_ascii=False)
        dict_str = f'''Refine the following JSON file\n```json\n''' + dict_str + f'''\n```'''
        pyperclip.copy(dict_str)
        print(f'The prompt for the word list {word_list} is in the clipboard.')


    def generate_eg_prompt(self, word_list:list):
        dict_str = json.dumps(self.abridge_dict_eg(word_list), ensure_ascii=False)
        dict_str = f'''You are a renowned German linguist. Your task is to complete the following JSON file by adding two suitable example sentences for each entry according to the definition and the usage of the words. Ensure your example sentences reflect the nuances of different meanings of the same headword. \n```json\n''' \
            + dict_str \
            + f'''\n```''' \
            + '\nFormat your response in a JSON code block.'
        pyperclip.copy(dict_str)
        print(f'The prompt for the word list {word_list} is in the clipboard.')

    
    def import_refined_dict(self, import_dict:dict):
        result_dict = dict()
        for headword in import_dict.keys():
            if headword in self.original_dict.keys():
                if headword not in self.refined_dict.keys():
                    original_entry_list = self.original_dict[headword]
                    new_entry_list = import_dict[headword]
                    if len(original_entry_list) == len(new_entry_list):
                        for i in range(len(new_entry_list)):
                            filtered_original_entry = {k:v for k, v in original_entry_list[i].items() if k not in new_entry_list[i].keys()}
                            new_entry_list[i].update(filtered_original_entry)
                        result_dict[headword] = deepcopy(new_entry_list)
                    else:
                        print(f'The number of definitions of the word {headword} does not match!')
                else:
                    print(f'The word {headword} has been refined.')
            else:
                print(f'The word {headword} does not exist in the original dictionary.')
        self.refined_dict.update(result_dict)
    

    def finish_import(self):
        with open(self.refined_dictionary_json, 'w') as json_file:
            json.dump(self.refined_dict, json_file, indent=4, ensure_ascii=False)

    
    def __abridge_dict_def(self, dict_whole:dict, word_list:list):
        dict_for_prompt = dict()
        for word in word_list:
            entry_list = dict_whole[word]
            abridged_entry_list = []
            for entry in entry_list:
                abridged_entry = dict()
                abridged_entry['Definition'] = ''
                abridged_entry['Anwendung'] = entry['Anwendung']
                abridged_entry['Beispiele'] = entry['Beispiele']
                abridged_entry_list.append(deepcopy(abridged_entry))
            dict_for_prompt[word] = deepcopy(abridged_entry_list)
        return dict_for_prompt
    

    def __abridge_dict_eg(self, dict_whole:dict, word_list:list):
        dict_for_prompt = dict()
        for word in word_list:
            entry_list = dict_whole[word]
            abridged_entry_list = []
            for entry in entry_list:
                abridged_entry = dict()
                abridged_entry['Definition'] = entry['Definition']
                abridged_entry['Anwendung'] = entry['Anwendung']
                abridged_entry['Beispiele'] = r'["", ""]'
                abridged_entry_list.append(deepcopy(abridged_entry))
            dict_for_prompt[word] = deepcopy(abridged_entry_list)
        return dict_for_prompt
    

    # def __abridge_dict_cn(self, dict_whole:dict, word_list:list):
    #     dict_for_prompt = dict()
    #     for word in word_list:
    #         entry_list = dict_whole[word]
    #         abridged_entry_list = []
    #         for entry in entry_list:
    #             abridged_entry = dict()
    #             abridged_entry['Definition'] = entry['Definition']
    #             abridged_entry['Anwendung'] = entry['Anwendung']
    #             abridged_entry['Chinesische Übersetzung'] = ''
    #             abridged_entry_list.append(deepcopy(abridged_entry))
    #         dict_for_prompt[word] = deepcopy(abridged_entry_list)
    #     return dict_for_prompt


