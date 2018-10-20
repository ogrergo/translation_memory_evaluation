class Operator:
    def __init__(self, param=None):
        self.param = param

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def preprocess(self, text, lang):
        return text, {'raw': text, 'language': lang}

    def postprocess(self, text, mapping, lang, mapping_tgt):
        return mapping['raw']