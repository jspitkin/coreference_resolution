from __future__ import division
from __future__ import print_function
import NounPhrase as np
import sys
import ioutil

def main():
    if len(sys.argv) != 3:
        print_usage()
        #return -1

    #listfile_path = sys.argv[1]
    #response_directory = sys.argv[2]

    print(ioutil.get_noun_phrases('dev/a8.txt'))

def print_usage():
    print("usage: python coreference.py <listfile> <responsedir>")

if __name__ == "__main__":
    main()
