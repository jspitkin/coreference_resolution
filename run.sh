chmod +x getenv.sh
./getenv.sh
source virtual_env/bin/activate
pip install nltk
python install_pickle.py
python coreference.py listfile.listfile response_files/
