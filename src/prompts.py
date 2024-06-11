sentence_prompt = 'You are a renowned German linguist. \
     Your task is to complete the following JSON file by adding two suitable example sentences for each entry according to the definition and the usage of the words. \
     Ensure your example sentences reflect the nuances of different meanings of the same headword.'

phrase_def_prompt = r'''You are a renowned German lexicographer. Given an incomplete JSON files, you are asked to complete the file by using a professional tone and simple German vocabulary to define the terms in concise full sentences. Write the definition beginning with "Wenn" that sets the context for the terms usage. For example, for the term "verbringen" write the definition "Wenn man etwas verbringt, bleibt man dort für eine bestimmte Zeit", where "Wenn man irgendwo eine bestimmte Zeit verbringt" provides the context in which "verbringen" is used, and "bleibt man dort für eine bestimmte Zeit" shows how "verbringen" is used in a practical sentence. 
Following the definition, craft an example sentence for the term. Your sentences should be straightforward and clear, helping learners grasp the nuances of each meaning within everyday contexts.
```json
{
    "term": {"Definition": "Definition of the term", "Beispiel": "Example sentence"}
}
```
'''

example_sentences_prompt = r'''As a German lexicographer, you're tasked with creating example sentences and fill-in-the-gap exercises for a given list of words. Craft sentences that are both educational and accessible to German learners. For each word, provide three example sentences demonstrating its usage. For words with multiple meanings, provide separate sentences to demonstrate each distinct usage. After providing each example sentences, create a fill-in-the-gap exercise by replacing the word with a blank `\\ldots`. Be mindful of separable verbs which might require two gaps. Format your response in a JSON file. 
For example, if the given list is ["kennenlernen"], you should respond
```json
{
    "kennenlernen": [
        {"example": "Auf der Party habe ich viele neue Leute kennengelernt.", "exercise": "Auf der Party habe ich viele neue Leute \\lldots."},
        {"example": "Im Sprachkurs lernt Maria die deutsche Kultur besser kennen.", "exercise": "Im Sprachkurs \\ldots Maria die deutsche Kultur besser \\lldots."}
        {"example": "Bei der internationalen Konferenz lernt Peter viele neue Kollegen kennen.", "exercise": "Bei der internationalen Konferenz \\ldots Peter viele neue Kollegen \\ldots."}
    ]
}
```'''