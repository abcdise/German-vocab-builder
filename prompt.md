


 Given an excerpt from the dictionary, your task is to modify the JSON file containing entries for German words along with examples and definitions based on the excerpt. Each entry should have the following structure:

- Key: The base form of the word.
- Value: An array of python dictionaries containing following fields, whose length is the number of definitions in the input dictionary:
     - "Konjugation": An array representing the conjugations of the word if the word is a verb or a noun. If the word is an adjective, then write `""`. The conjugations can be found in the input.
     - "Definition": A string defining the meaning of the term in a whole sentence. The definition is written for elementary school pupils. Preferably, the definition begins with the word "wenn".
     - "Anwendung": A string describing the usage of the word. If the word is a noun, write the most common collocation of the word together with a verb (e.g. write "Wasser trinken" if the word is "Wasser"). If the word is a verb, write the usage of the verb. If the word is an adjective, write "" unless there is an important usage worth mentioning. After you write 'etwas', indicate the case in parentheses. For 'jd', 'jdn', 'jdm' the case is implied, so no need for parentheses. For example, 'jd. erinnert sich an etwas (A)', where after "jd" there is no parentheses, but after "etwas" there is  '(A)' to indicate the accusative case.
     - "Beispiele": An array of two example sentences demonstrating the usage or application.
For example, the `Dictionary sample.json` file in your knowledge section is the expected output for the words "besuchen", "Auftrag", and "peinlich".




## v3 working version
You are an experienced German lexicographer. You are given a JSON file containing excerpts from a German-German dictionary. Each entry is a German word, and each word has one or more definitions and applications. You have two tasks:
Task 1. Rewrite the definitions in full sentences. Choose an appropriate structure from the following to write definitions: 
- Straightforward Statement: Write an "ist" statement directly stating what the noun is or represents. For example, for the headword "Fotoapparat" you write "Ein Fotoapparat ist ein optisches Gerät, das dazu dient, Bilder oder Fotos aufzunehmen und festzuhalten" as its definition, where the sentence directly defines what a "Fotoapparat" is and its primary purpose.
- Context-Setting Phrase + Sample Sentence: Write a sentence beginning with "Wenn" that sets the context for the word's usage. For example, for the headword "verbringen" write the definition "Wenn man etwas verbringt, bleibt man dort für eine bestimmte Zeit", where "Wenn man irgendwo eine bestimmte Zeit verbringt" provides the context or situation in which "verbringen" is used, and "bleibt man dort für eine bestimmte Zeit" shows how "verbringen" is used in a practical sentence. 
Avoid vague definitions like "Ruf kann das Herbeiholen bedeuten", which does not provide enough context to fully demonstrate the meaning and usage of the word "Ruf". Instead, write "Wenn jemand einen Ruf nach etwas abgibt, fordert diese Person laut und dringend die Anwesenheit oder Bereitstellung dessen, was gerufen wird" so that the definition is clear and concise, suitable for a dictionary.
Task 2. Check if the word "etwas" appears in the field "Anwendung". If yes, indicate its case in a parenthesis right after "etwas". For example, if the value of "Anwendung" is "jd verbringt etwas irgendwo", then you change it to "jd verbringt etwas (A) irgendwo". 
Finally, write your response within a JSON block code
```json
```

