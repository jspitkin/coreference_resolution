import nltk

def main():
    test = "Hello World. This is a long sentence"
    tokens = nltk.word_tokenize(test)
    print(tokens)

if __name__ == "__main__":
    main()
