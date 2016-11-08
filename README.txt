Jake Pitkin - u0891770
Curtis Clements - u0764479

Natural Language Processing
Initial System Evaluation #1

Our coreference resolution system is written using Python3. A virtual enviorment is not required to run our system on the CADE machines.
This was tested on CADE machine lab1-18.

== To Run ==
From any CADE machine run "sh run.sh". 
This will install the 'average_perceptron_tagger' module for nltk.
Also, this will run our system against all 15 of the provided .crf files which are listed all_files.listfile.
The .crf files are located in ./scoring/dev/
The response files will be placed in ./scoring/response_files/
