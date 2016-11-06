import nltk
import re

def get_file_as_string(path):
    with open(path, 'r') as file:
        file_input = file.read().replace('\n', ' ')
    return file_input

def get_noun_phrases(path):
    tokens = nltk.word_tokenize(get_file_as_string(path))
    tokens_with_pos_tag = nltk.pos_tag(tokens)
    grammar = """
                NP: {<DT|PP\$>?<JJ>*<NN>}
                    {<NNP>+}
                    {<NN>+}
    """
    chunker = nltk.RegexpParser(grammar)
    result = chunker.parse(tokens_with_pos_tag)
    noun_phrases = []
    for subtree in result.subtrees(filter=lambda t: t.label() == 'NP'):
        noun_phrase = ""
        for word in subtree.leaves():
            noun_phrase += word[0] + " "
        noun_phrases.append(noun_phrase.strip())
    return noun_phrases

def get_initial_anaphora_list(path):
    noun_phrase_list = []
    file_string = get_file_as_string(path)
    matches = re.findall('<COREF ID="[\d]+">[a-zA-Z\d\s-]+<\/COREF>', file_string, re.DOTALL)
    for match in matches:
        noun_phrase = re.findall('<COREF ID="[\d]+">(.*?)<\/COREF>', match)
        noun_id = re.findall('<COREF ID="(.*?)">', match)
        if len(noun_phrase) > 0 and len(noun_id) > 0:
            pair = (noun_id[0], noun_phrase[0])
            noun_phrase_list.append(pair)
    return noun_phrase_list
