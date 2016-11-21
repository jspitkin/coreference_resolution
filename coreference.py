import NounPhrase as np
import sys
import ioutil
import nltk

nltk.download("punkt")


def main():
    if len(sys.argv) != 3:
        print_usage()
        return -1

    listfile_path = sys.argv[1]
    response_directory = sys.argv[2]

    for path in ioutil.get_files_to_check(listfile_path):
        path = path.strip('\n')
        noun_phrases = ioutil.get_noun_phrases(path)
        anaphora_list = ioutil.get_initial_anaphora_list(path)
        # Testing for phrases that contain parts of other phrases
        relevant_noun_phrases = ioutil.get_relevant_noun_phrases(anaphora_list, noun_phrases)
        nps = ioutil.get_noun_phrase_positions(path, relevant_noun_phrases)
        combined_list = ioutil.combine_anaphora_relevant_np(anaphora_list, nps)

        # Remove common words from the noun phrases
        combined_list = ioutil.remove_common_words(combined_list)

        ioutil.assign_previous(combined_list)
        ioutil.assign_refs_for_similars(combined_list)
        ioutil.it_assigner(combined_list)
        ioutil.assign_refs_for_pronouns(combined_list)

        # Check dates
        #ioutil.assign_date_to_today(combined_list, ioutil.get_noun_phrase_positions(path, noun_phrases))

        # Writing out the final file, all attempts at assignment should be combined before this
        ioutil.write_response_file(response_directory, path, combined_list)

def print_usage():
    print("usage: python coreference.py <listfile> <responsedir>")

if __name__ == "__main__":
    main()
