import pyperclip
from abc import ABC, abstractmethod
from copy import deepcopy
import random
import prompts
import json
from pathlib import Path
import string

def remove_punctuation(input_string):
    # Create translation table
    translator = str.maketrans('', '', string.punctuation)
    
    # Remove punctuation using translation table
    return input_string.translate(translator)

def detect_solution(original_text: str, manipulated_text: str) -> list:
    original_text_list = original_text.split(' ')
    manipulated_text_list = manipulated_text.split(' ')
    # Find the index of the word that has been replaced by \\ldots in manupulated_text
    index = [i for i, j in enumerate(manipulated_text_list) if r'\ldots' in j]
    # Find the word that has been replaced by \\ldots in original_text
    return [remove_punctuation(original_text_list[i]) for i in index]


def json_string_to_dict(json_string: str):
    try:
        # Convert the JSON string to a Python dictionary
        python_dict = json.loads(json_string)
        return python_dict
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None


class Exercise(ABC):

    def __init__(self, word_list:list):
        self.word_list = word_list
        self.generation_prompt = None
        self.exercise: str = None
        self.exercise_dict: dict = dict()
        self.solution: str = None


    @abstractmethod
    def finish_import(self):
        pass


    def get_prompt(self):
        if self.generation_prompt is not None:
            pyperclip.copy(self.generation_prompt)
        else:
            print('There is no prompt yet.')


    def import_exercise(self, text:str):
        self.exercise = self._string_processing(text)

    
    def import_solution(self, text:str):
        self.solution = self._string_processing(text)


    def _string_processing(self, text):
        '''
        Parse strings
        '''
        text = self.__unify_quotes(text)
        text = self.__replace_en_dashes(text)
        text = self.__replace_quotes(text)
        text = self.__replace_pounds(text)
        return text
    

    def __unify_quotes(self, text):
        text = text.replace("’", "'")
        text = text.replace("‘", "'")
        text = text.replace("“", '"')
        text = text.replace("”", '"')
        return text
                            

    def __replace_quotes(self, text):
        text_list = text.split(' ')
        text_list_new = []
        for word in text_list:
            if word.startswith("'"):
                word = '`' + word[1:]
            text_list_new.append(word)
        return ' '.join(text_list_new)


    def __replace_pounds(self, text):
        return text.replace('£', r'\pounds')


    def __replace_en_dashes(self, text):
        return text.replace('–', '--')
    

    def _write_box(self, word_list:list):
        shuffled_word_list = deepcopy(word_list)
        shuffled_word_list = self._remove_duplicates(shuffled_word_list)
        random.shuffle(shuffled_word_list)
        return r' \qquad '.join(shuffled_word_list)
    

    def _remove_duplicates(self, data: list):
        return list(set(data))


class Definition(Exercise):
    '''
    A class representing a definition exercise.

    Inherits from the Exercise class.

    Attributes:
    - word_list (list): A list of words for which the definitions need to be imported.
    - definition (str): The formatted definitions and examples from the dictionary.
    - exercise (str): The fill-in-the-gap exercise generated from the examples.
    - solution (str): The solutions for the fill-in-the-gap exercise.

    Methods:
    - import_definition_from_dictionary: Imports definitions and examples from the dictionary and generates the fill-in-the-gap exercise.
    - finish_import: Adds the definition, exercise, and solution to the exercise dictionary.
    '''

    def __init__(self, word_list: list):
        super().__init__(word_list)
        self.definition = None
        self.definition_dict = dict()

    def import_definition_from_dictionary(self, dictionary_path:str='../../../../../Library/Mobile Documents/com~apple~CloudDocs/Projects/Vocab Builder/German/Dictionary/Refined PONS.json') -> None:
        '''
        The method looks for the words in the dictionary and write the definitions and the examples from the dictionary as a form
        that the LaTeX template is expecting. In the end, the methods gathers the examples and makes the fill-in-the-gap exercise.

        Args:
        - dictionary_path (str): The path of the json file that saves the dictionary.
        '''
        dictionary_json = Path(dictionary_path)
        try:
            with open(dictionary_json) as json_file:
                dictionary = json.load(json_file)

            def_text = ''
            for word in self.word_list:
                if word in dictionary:
                    def_text += r'\vocabulary{' + word + r'}'
                    def_text += r'{}' + '\n'
                    for entry in dictionary[word]:
                        forms = r'\trianglebullet ' + entry['Formen']
                        if forms != r'\trianglebullet ':
                            forms += ';'
                        def_text += r'\gerdefitem{' + forms + r'}'
                        usage = entry['Anwendung']
                        if usage:
                            usage += ';'
                        def_text += r'{' + usage + r'}'
                        definition = entry['Definition']
                        definition = self._string_processing(definition)
                        def_text += r'{' + definition + r'}'
                        if entry['Beispiele']:
                            sentence = entry['Beispiele'][0]
                            sentence = self._string_processing(sentence)
                            def_text += r'{' + sentence + r'}' + '\n'
                        else:
                            # If there is no example sentence, we still need a `{}` for the LaTeX command.
                            def_text += r'{}' + '\n'
                else:
                    print(f'The word {word} does not exist in the dictionary.')

            self.definition = def_text # No need to preprocess the string because it has be done in the for loop


        except FileNotFoundError:
            print(f"The dictionary file '{dictionary_json}' does not exist.")

    def finish_import(self):
        self.exercise_dict['definition'] = self.definition


class ExampleSentences(Exercise):
    example_sentences: dict = dict()
    example_sentences_with_analysis: dict = dict()

    def create_prompt(self, number_of_sentences:str):
        prompt = prompts.example_sentences_prompt + '\n'
        prompt += f'For each word in the list {self.word_list}, provide {number_of_sentences} example sentences and the corresponding fill-in-the-gap exercises.'
        self.generation_prompt = prompt

    
    def import_sentences(self, text: str):
        self.import_exercise(text)
        self.example_sentences = json.loads(self.exercise)


    def get_second_prompt(self):
        prompt = ''
        return prompt

    
    def import_sentence_analysis(self, text: str):
        self.example_sentences_with_analysis = dict()


    def finish_import(self):
        None
        # tex_str = r'''\begin{enumerate}
        
        # '''
        # for sentence in self.example_sentences.values():
        #     tex_str += r'\item ' + f'{sentence}\n'
        # tex_str += r'\end{enumerate}'
        # self.exercise_dict['sentences'] = tex_str
        

class FillInTheGapExercise(Exercise):

    def __init__(self, word_list:list, example_sentences: ExampleSentences):
        super().__init__(word_list=word_list)
        self.word_list = word_list
        self.box = self._write_box(word_list=self.word_list)
        self.example_sentences = example_sentences.example_sentences
        self.exercise, self.solution = self.generate_exercise(aug_dict=self.example_sentences)
 

    def finish_import(self):
        self.exercise_dict['exercise'] = self.exercise
        self.exercise_dict['box'] = self.box
        self.exercise_dict['solution'] = self.solution

    
    def generate_exercise(self, aug_dict: dict):
        exercise_list = []
        for word, sentence_list in aug_dict.items():
            for original_sentence in sentence_list:
                question = original_sentence['exercise']
                sol_list = detect_solution(original_text=original_sentence['example'],
                                           manipulated_text=question)   
                exercise_list.append((question, ', '.join(sol_list)))
    
        random.shuffle(exercise_list)
        ex = r'\begin{enumerate}' + '\n'
        sol = r'\begin{enumerate}' + '\n'
        for exercise in exercise_list:
            ex += r'\item ' + exercise[0] + '\n'
            sol += r'\item ' + exercise[1] + '\n'

        ex += r'\end{enumerate}' + '\n'
        sol += r'\end{enumerate}' + '\n'

        return ex, sol


    def generate_solution(self, aug_dict: dict):
        None
    

class DialogueExercise(Exercise):
    """
    Represents a dialogue exercise for vocabulary building.

    Args:
        word_list (list): A list of words for the exercise.

    Attributes:
        phrase_dict (dict): A dictionary containing phrases and their definitions.
        abridged_phrase_dict (dict): A dictionary containing abridged phrases and their definitions.
        box (str): The write box for the exercise.
        exercise (str): The generated exercise.
        solution (str): The solution for the exercise.

    Methods:
        __import_dictionary: Imports the dictionary of phrases.
        create_prompt: Creates the prompt for the exercise.
        generate_exercise: Generates the exercise based on the dialogue dictionary.
        finish_import: Finishes the import process.

    """

    def __init__(self, word_list: list):
        super().__init__(word_list=word_list)
        self.phrase_dict = dict()
        self.abridged_phrase_dict = dict()
        self.__import_dictionary()
        self.create_prompt()
        self.box = self._write_box(word_list=word_list)
        self.exercise = None
        self.solution = None

    
    def __import_dictionary(self, dictionary_path:str='../../../../../Library/Mobile Documents/com~apple~CloudDocs/Projects/Vocab Builder/German/Dictionary/Phrase.json'):
        """
        Imports the dictionary of phrases.

        Args:
            dictionary_path (str): The path to the dictionary file. Default is the relative path to the Phrase.json file.

        Raises:
            FileNotFoundError: If the dictionary file does not exist.

        """
        try:
            with open(dictionary_path) as file:
                self.phrase_dict = json.load(file)
            for word in self.word_list:
                if word in self.phrase_dict.keys():
                    self.abridged_phrase_dict[word] = self.phrase_dict[word][0]['Definition']
                else:
                    raise ValueError(f'The term {word} does not exist in the reference dictionary.')
        except FileNotFoundError:
            raise FileNotFoundError(f"The dictionary file '{dictionary_path}' does not exist.")
    

    def create_prompt(self):
        """
        Creates the prompt for the exercise.

        """
        prompt = prompts.dialogue_exercise_prompt
        prompt += 'Create the JSON file based on the following inputs'
        prompt += json.dumps(self.abridged_phrase_dict, ensure_ascii=False)
        self.generation_prompt = prompt


    def generate_exercise(self, dialogue_dict:dict):
        """
        Generates the exercise based on the dialogue dictionary.

        Args:
            dialogue_dict (dict): A dictionary containing dialogues.

        """
        ex = ''
        sol = r'\begin{enumerate}' + '\n'
        index = 1
        for _, dialogue in dialogue_dict.items():
            ex += r'\noindent \textbf{Dialog ' + str(index) + '}\n'
            ex += r'\vspace{-1ex}' + '\n'
            ex += r'\begin{dialogue}' '\n'
            ex += r'\speak{A} ' + dialogue['A'] + '\n'
            ex += r'\speak{B} ' + dialogue['Paraphrase'] + '\n'
            ex += r'\end{dialogue}' + '\n'
            ex += r'\underline{\textsc{' + dialogue['Keyword'] + '}}\n'
            ex += r'\vspace{10ex}' + '\n\n'
            sol += r'\item ' + dialogue['B']  + '\n'
            index += 1

        sol += r'\end{enumerate}' + '\n'
        self.exercise = ex
        self.solution = sol

    
    def finish_import(self):
        """
        Finishes the import process.

        """
        self.exercise_dict['exercise'] = self.exercise
        self.exercise_dict['solution'] = self.solution
        

class ExerciseFactory:
    def create_exercise(self, exercise_type:str, word_list:list, example_sentences: ExampleSentences=None):
        '''
        Create exercises.

        Args:
            exercise_type (str): The type of exercise to create.
            word_list (list): A list of words for the exercise.
            example_sentences (ExampleSentences, optional): An instance of ExampleSentences class. Defaults to None.

        Returns:
            Exercise: An instance of the corresponding exercise class.

        Raises:
            ValueError: If the exercise type is invalid.
        '''
        if exercise_type == 'Fill in the gap':
            return FillInTheGapExercise(word_list=word_list, example_sentences=example_sentences)
        elif exercise_type == 'Definition':
            return Definition(word_list=word_list)
        elif exercise_type == 'Dialogue':
            return DialogueExercise(word_list=word_list)
        raise ValueError('Invalid exercise type!')
    

class ExerciseGatherer:
    """
    A class that represents an exercise gatherer.

    Attributes:
        exercise_set (list): A list to store exercises.

    Methods:
        import_exercise: Imports an exercise and adds it to the exercise set.
        get_exercise_set: Retrieves an exercise set based on the set index.
        _int_to_roman: Converts an integer to a Roman numeral.
    """

    def __init__(self):
        """
        Initializes an ExerciseGatherer object with an empty exercise set.
        """
        self.exercise_set = []

    def import_exercise(self, exercise):
        """
        Imports an exercise and adds it to the exercise set.

        Args:
            exercise (Exercise): The exercise to be imported.

        Returns:
            None
        """
        exercise_ = deepcopy(exercise)
        self.exercise_set.append(exercise_)

    def get_exercise_set(self, set_index, last_set=True):
        """
        Retrieves an exercise set based on the set index.

        Args:
            set_index (int): The index of the exercise set.
            last_set (bool): Flag indicating whether to retrieve the last set or not.

        Returns:
            tuple: A tuple containing the set index (in Roman numeral) and the exercise set.
        """
        if last_set:
            return self._int_to_roman(set_index), self.exercise_set[-1]
        else:
            return self._int_to_roman(set_index), self.exercise_set[set_index-1]

    def _int_to_roman(self, num):
        """
        Converts an integer to a Roman numeral.

        Args:
            num (int): The integer to be converted.

        Returns:
            str: The Roman numeral representation of the integer.
        """
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syms = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_numeral = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_numeral += syms[i]
                num -= val[i]
            i += 1
        return roman_numeral