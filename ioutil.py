import nltk
import re
import NounPhrase as np
from nltk.corpus import names
import random

def get_file_as_string(path):
    with open(path, 'r') as file:
        file_input = file.read().replace('\n', ' ')
    return file_input

def get_nounfile_as_string(path):
    with open(path, 'r') as file:
        file_input = file.read()
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
        response_string +=  '<COREF ID="' + str(response.id) + '"'
        if response.ref is not None:
            response_string += ' REF="' + str(response.ref) + '"'
        response_string +='>' + response.noun_phrase + "</COREF>\n"
    response_string += "</TXT>"
    with open(path, 'w+') as file:
        file.write(response_string)

def get_noun_phrases(path):

    document = get_file_as_string(path)
    document = document.replace("</COREF>", "")
    document = document.replace("COREF ID=", "")

    paragraphs = [p for p in document.split('\n') if p]

    noun_phrases = []

    for paragraph in paragraphs:

        tokens = nltk.word_tokenize(paragraph)
        tokens_with_pos_tag = nltk.pos_tag(tokens)
        grammar = """
                    NP: {<DT|PP\$>?<JJ>*<NN>}
                        {<NNP>+}
                        {<NN>+}
                        {<PRP><NN>}
                        {<PRP$>}
                        {<NNP><NNS>}
                        {<DT><NNP>}
                        {<DT><CD><NNS>}
                        {<CD><NNS>}
                        {<NNS>+}
                        {(<DT>?<RB>?)?<JJ|CD>*(<JJ|CD><,>)*<NN.*>+}
                        {(<DT|PRP.>?<RB>?)?<JJ|CD>*(<JJ|CD><,>)*(<NN.*>)+}
                        {<WP>}
                        {<NNP><POS><NNP>}

        """
        chunker = nltk.RegexpParser(grammar)
        result = chunker.parse(tokens_with_pos_tag)
        # print (result)

        for subtree in result.subtrees(filter=lambda t: t.label() == 'NP'):
            noun_phrase = ""
            for word in subtree.leaves():
                noun_phrase += word[0] + " "
            if '>' in noun_phrase or '<' in noun_phrase:
                    continue
            noun_phrases.append(noun_phrase.strip())

    # Add all dates in the format dd/mm/yy as noun phrases
    match = re.findall(r'(\d+/\d+/\d+)', document)
    for m in match:
        noun_phrases.append(m)

    return noun_phrases

def remove_common_words(noun_phrases):
    remove_words = ['a', 'an', 'the', 'and', 'of', 'at', 'in', 'of', 'only', 'on', '>', '<']
    return_list = []
    for np in noun_phrases:
        np_split = (np.noun_phrase).split()
        result_np = [word for word in np_split if word.lower() not in remove_words]
        result = ' '.join(result_np)
        np.noun_phrase = result
        if len(np.noun_phrase.strip()) != 0 and np.noun_phrase != "i":
            return_list.append(np)
    return return_list
                 
def get_initial_anaphora_list(path):
    noun_phrase_list = []
    file_string = get_file_as_string(path)

    pattern = '<COREF ID="[\d]+">(.*?)<\/COREF>'
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
            item.anaphora = True
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
    coref_set.add("he")
    coref_set.add("she")
    coref_set.add("her")
    coref_set.add("his")
    coref_set.add("we")
    coref_set.add("they")
    coref_set.add("our")


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

    first_found_anaphora_id = int(anaphora_list[0].id)
    noun_phrase_list = sorted(noun_phrase_list, key=lambda x: x.end_index)
    anaphora_list = sorted(anaphora_list, key=lambda x: x.end_index)

    id_index = 1
    for np in noun_phrase_list:
        already_in_list = False
        for anaphora in anaphora_list:
            if np.start_index > anaphora.start_index and np.end_index < anaphora.end_index:
                already_in_list = True
        if not already_in_list:
            np.id = 'X' + str(id_index)
            np.ref = first_found_anaphora_id
            id_index += 1
            combined_list.append(np)
    for np in anaphora_list:
        combined_list.append(np)
    sorted_combined_list = sorted(combined_list, key=lambda x: x.start_index)
    return sorted_combined_list

def assign_refs_for_pronouns(sorted_combined_list):
    current_anaphora = None
    pronouns = ['he', 'she', 'it', 'her', 'him', 'they']
    assigned_match = False
    for index, np, in enumerate(sorted_combined_list):
        if current_anaphora is None:
            if np.anaphora:
                current_anaphora = np
            else:
                continue
        if np.anaphora is True:
            assigned_match = False
            current_anaphora = np
            continue
        if (np.noun_phrase).lower().strip() in pronouns:
            assigned_match = True
            np.ref = current_anaphora.id

def assign_previous(anaphora_list):
    previous_item = None
    for item in anaphora_list:
        if item.anaphora is False:
            continue
        if previous_item is None:
            previous_item = item
        else:
            item.ref = previous_item.id
            previous_item = item

def assign_refs_for_similars(sorted_combined_list):
    for index, np, in enumerate(sorted_combined_list):
        if np.noun_phrase == 'he' or np.noun_phrase == 'she' or np.noun_phrase == 'it':
            continue
        np_words = np.noun_phrase.split()
        np_lower = [x.lower() for x in np_words]
        np_contained_words = set(np_lower)

        for inner_np in sorted_combined_list[index+1:]:
            inner_np_list = inner_np.noun_phrase.split()
            for s in inner_np_list:
                if(s.lower() in np_contained_words):
                    inner_np.ref = np.id
                    if np.similar is False:
                        np.ref = inner_np.id
                        np.similar = True

def assign_date_to_today(sorted_combined_list, noun_phrases):

    id_index = 1;
    dates = ["today"]

    for np in noun_phrases:
        match = re.findall(r'(\d+/\d+/\d+)', np.noun_phrase)
        if match:
            np.id = 'Q' + str(id_index)
            id_index += 1
            for nounp in sorted_combined_list:
                if nounp.noun_phrase  in dates :
                    if(np.start_index < nounp.start_index):
                        nounp.ref=np.id
                        sorted_combined_list.append(np)
                    # Ignore the else case for now...crf files have a date at the top
                    # that is later referred to as "today"
                    # else:
                    #     np.ref=nounp.id
                    #     sorted_combined_list.append(np)

    sorted_combined_list = list(set(sorted_combined_list))
    return sorted_combined_list

def get_response_noun_phrases(assigned_list):
    responses = set()
    related_ids = set()
    for item in assigned_list:
        if item.ref is not None:
            responses.add(item)
            related_ids.add(item.ref)
    for item in assigned_list:
        if item.id in related_ids:
            responses.add(item)
    response = list(responses)
    return response

def gender_features(word):
    features = {}
    features["last_letter"] = word[-1].lower()
    return features

def gender_assign_name(name):
    labeled_names = ([(name, 'male') for name in names.words('male.txt')]
    + [(name, 'female') for name in names.words('female.txt')])
    random.shuffle(labeled_names)
    featuresets = [(gender_features(n), gender) for (n, gender) in labeled_names]
    train_set, test_set = featuresets[500:], featuresets[:500]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    return(classifier.classify(gender_features(name)))

def it_assigner(combined_list):
    male_pronouns = ["he","him"]
    female_pronouns = ["she", "her"]
    pronouns_it = ["it", "its", "it's", "him"]

    combined_list = sorted(combined_list, key=lambda x: x.start_index)
    prev_np = None


    for np in combined_list:
        if np.noun_phrase in pronouns_it:
            np.gender = "it"
            if prev_np is not None:
                np.ref = prev_np.id
        prev_np = np

def get_appositives(path):
    appositives_list = []
    file_string = get_file_as_string(path)
    pattern = '[,]* <COREF ID="[\d]+">(.*?)<\/COREF>[,.]*'
    regex = re.compile(pattern, re.IGNORECASE)
    for m in regex.finditer(file_string):
        noun_id = re.findall('<COREF ID="(.*?)">', m.group())
        noun_phrase = re.findall('[\,] <COREF ID="[\d]+">(.*?)<\/COREF>[\,]', m.group())
        if len(noun_phrase) > 0 and len(noun_id) > 0:
            item = np.NounPhrase()
            item.noun_phrase = noun_phrase[0]
            item.id = noun_id[0]
            item.start_index = m.start()
            item.end_index = m.end()
            item.anaphora = "app"
            appositives_list.append(item)
            #print(item.noun_phrase)

    return appositives_list

def match_appositive_and_np(appositives_list, noun_phrase_list, combined_list2):

    combined_list = []
    real_appositives = []
    for np in appositives_list:
        combined_list.append(np)
    for np in noun_phrase_list:
        combined_list.append(np)

    id_index = 1

    combined_list = sorted(combined_list, key=lambda x: x.start_index)

    prev_np = None

    for np in combined_list:
        if np.anaphora == "app":

            prev_np.id = 'A' + str(id_index)
            id_index += 1
            np.ref = prev_np.id
            real_appositives.append(np)
            real_appositives.append(prev_np)

        prev_np = np

    for np in real_appositives:
        for np2 in combined_list2:
            if np.id == np2.id:
                np2.ref = np.ref
            elif "A" in np.id:
                combined_list2.append(np)

    #something is wrong here, thousands of lines are getting added :(
    combined_list2 = list(set(combined_list2))

    return combined_list2





