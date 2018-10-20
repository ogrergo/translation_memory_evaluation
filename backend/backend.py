

class Backend:
    def __init__(self, params):
        self.params = params

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def find(self, text, lang):
        pass

    def add(self, text_src, mapping_src, text_tgt, mapping_tgt, direction, id):
        pass

    def load(self, dataset, operator):
        pass