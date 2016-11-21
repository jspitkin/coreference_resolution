class NounPhrase:
    def __init__(self):
        self.noun_phrase = None
        self.ref = None
        self.id = None
        self.start_index = None
        self.end_index = None
        self.gender = None
        self.anaphora = False

    def __str__(self):
        return_string = ""
        if self.noun_phrase is not None:
            return_string += self.noun_phrase + " "
        if self.id is not None:
            return_string += str(self.id) + " "
        if self.ref is not None:
            return_string += str(self.ref) + " "
        if self.start_index is not None:
            return_string += str(self.start_index) + " "
        if self.end_index is not None:
            return_string += str(self.end_index) + " "
        return return_string.strip()
