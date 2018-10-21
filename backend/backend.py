

class Backend:
    def __init__(self, paramaters):
        self.parameters = paramaters

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def find(self, sentence):
        pass

    def add(self, sentence_src, sentence_tgt):
        pass

    def load(self, dataset):
        pass
