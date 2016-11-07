import nltk
import re
import NounPhrase as np

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
            item = np.NounPhrase()
            item.noun_phrase = noun_phrase[0]
            item.id = noun_id[0]
            item.start_index = m.start()
            item.end_index = m.end()
            noun_phrase_list.append(item)
    return noun_phrase_list

def get_noun_phrase_positions(path, noun_phrases):
    noun_phrase_list = []
    noun_phrase_set = set(noun_phrases)
    file_string = get_file_as_string(path)

    for noun_phrase in noun_phrase_set:
        pattern = re.escape(noun_phrase)
        regex = re.compile(pattern, re.IGNORECASE)

        for m in regex.finditer(file_string):
            phrase = m.group()
            if len(phrase) > 0:
                item = np.NounPhrase()
                item.noun_phrase = phrase
                item.start_index = m.start()
                item.end_index = m.end()
                noun_phrase_list.append(item)
    return noun_phrase_list

def get_relevant_noun_phrases(coref_list, noun_phrase_list):
    coref_set = set()
    relevant_noun_phrases = []
    for noun_phrase in coref_list:
        words = noun_phrase.noun_phrase.split()
        for word in words:
            coref_set.add(word.lower())
    for noun_phrase in noun_phrase_list:
        words = noun_phrase.split()
        for word in words:
            if word.lower() in coref_set:
                relevant_noun_phrases.append(noun_phrase)
                break
    return relevant_noun_phrases

def combine_anaphora_relevant_np(anaphora_list, noun_phrase_list):
    combined_list = []
    id_index = 1
    for np in noun_phrase_list:
        already_in_list = False
        for anaphora in anaphora_list:
            if np.start_index > anaphora.start_index and np.end_index < anaphora.end_index:
                already_in_list = True
        if not already_in_list:
            np.id = 'X' + str(id_index)
            id_index += 1
            combined_list.append(np)
    for np in anaphora_list:
        combined_list.append(np)
    sorted_combined_list = sorted(combined_list, key=lambda x: x.start_index)
    return sorted_combined_list
   # return combined_list.sort(key=lambda x: x.start_index)

def assign_refs_for_similars(sorted_combined_list):



    for index, np, in enumerate(sorted_combined_list):

        np_words = np.noun_phrase.split()
        np_lower = [x.lower() for x in np_words]
        np_contained_words = set(np_lower)

        if("a" in np_contained_words):
            np_contained_words.remove("a")
        if("the" in np_contained_words):
            np_contained_words.remove("the")
        for inner_np in sorted_combined_list[index+1:]:
            inner_np_list = inner_np.noun_phrase.split()
            for s in inner_np_list:
                if(s.lower() in np_contained_words and inner_np.ref is None):
                    inner_np.ref = np.id
    return sorted_combined_list


