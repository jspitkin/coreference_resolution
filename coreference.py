from __future__ import division
from __future__ import print_function
import NounPhrase as np
import sys
import ioutil

def main():
    if len(sys.argv) != 3:
        print_usage()
        return -1

    listfile_path = sys.argv[1]
    response_directory = sys.argv[2]

    responses = []
    response = np.NounPhrase()
    response.noun_phrase = "Jake"
    response.coref = 2
    response.id = 1
    responses.append(response)
    response = np.NounPhrase()
    response.noun_phrase = "Curtis"
    response.coref = 4
    response.id = 3
    responses.append(response)

    for path in ioutil.get_files_to_check(listfile_path):
        ioutil.write_response_file(response_directory, path, responses)

    noun_phrases = ioutil.get_noun_phrases('dev/b9.txt')
    anaphora_list = ioutil.get_initial_anaphora_list('dev/b9.crf')

    ioutil.get_relevant_noun_phrases(anaphora_list, noun_phrases)

def print_usage():
    print("usage: python coreference.py <listfile> <responsedir>")

if __name__ == "__main__":
    main()
