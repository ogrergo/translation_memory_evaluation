from mosestokenizer import MosesPunctuationNormalizer

from TM2.operators.operator import Operator


class MosesPreprocess(Operator):
    def __init__(self, param=None):
        super().__init__(param=param)

        self.tokenizers = {
            'fr': MosesPunctuationNormalizer('en'), MosesTokenizer('en')
        }

    def preprocess(self, text, lang):
        text, mapping = super().preprocess(text, lang)
        return text, mapping

    def postprocess(self, text, mapping, lang, mapping_tgt):
        pass