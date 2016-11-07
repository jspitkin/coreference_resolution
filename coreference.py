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

    noun_phrases = ioutil.get_noun_phrases('dev/b9.txt')
    anaphora_list = ioutil.get_initial_anaphora_list('dev/b9.crf')
    relevant_noun_phrases = ioutil.get_relevant_noun_phrases(anaphora_list, noun_phrases)
    nps = ioutil.get_noun_phrase_positions('dev/b9.crf', relevant_noun_phrases)
    # for np in nps:
    #     print(np)
    combined_list = ioutil.combine_anaphora_relevant_np(anaphora_list, nps)


    combined_list = ioutil.assign_refs_for_similars(combined_list)
    for np in combined_list:
        print(np)

    ioutil.get_relevant_noun_phrases(anaphora_list, noun_phrases)

def print_usage():
    print("usage: python coreference.py <listfile> <responsedir>")

if __name__ == "__main__":
    main()
