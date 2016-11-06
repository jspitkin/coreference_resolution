import nltk
import re

def get_file_as_string(path):
    with open(path, 'r') as file:
        file_input = file.read().replace('\n', ' ')
    return file_input

def get_files_to_check(path):
    files_to_check = []
    with open(path, 'r') as file:
        for line in file:
            files_to_check.append(line)
    return files_to_check

def write_response_file(response_directory, crf_path, responses):
    path = response_directory + crf_path.split('/')[-1].split('.')[0] + ".response"
    response_string = "<TXT>\n"
    for response in responses:
        response_string +=  '<COREF ID="' + str(response.id) + ' REF="' + str(response.coref) + '">' + response.noun_phrase + "</COREF>\n"
    response_string += "</TXT>"

    with open(path, 'w') as file:
        file.write(response_string)

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

    pattern = '<COREF ID="[\d]+">[a-zA-Z\d\s-]+<\/COREF>'
    regex = re.compile(pattern, re.IGNORECASE)

    for m in regex.finditer(file_string):
        noun_id = re.findall('<COREF ID="(.*?)">', m.group())
        noun_phrase = re.findall('<COREF ID="[\d]+">(.*?)<\/COREF>', m.group())
        if len(noun_phrase) > 0 and len(noun_id) > 0:
            pair = (noun_id[0], noun_phrase[0], m.start(), m.end())
            noun_phrase_list.append(pair)
        noun_phrase_list.append(pair)
    return noun_phrase_list

def get_noun_phrase_positions(path, noun_phrases):
    noun_phrase_list = []
    file_string = get_file_as_string(path)

    for noun_phrase in noun_phrases:
        pattern = re.escape(noun_phrase)
        regex = re.compile(pattern, re.IGNORECASE)

        for m in regex.finditer(file_string):
            phrase = m.group()
            if len(phrase) > 0:
                pair = (phrase, m.start(), m.end())
                noun_phrase_list.append(pair)
    return noun_phrase_list

def get_relevant_noun_phrases(coref_list, noun_phrase_list):
    coref_set = set()
    relevant_noun_phrases = []
    for noun_phrase in coref_list:
        words = noun_phrase[1].split()
        for word in words:
            coref_set.add(word.lower())
    for noun_phrase in noun_phrase_list:
        words = noun_phrase.split()
        for word in words:
            if word.lower() in coref_set:
                relevant_noun_phrases.append(noun_phrase)
                break
    return relevant_noun_phrases
