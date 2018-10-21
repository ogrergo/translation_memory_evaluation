from mosestokenizer import MosesPunctuationNormalizer, MosesTokenizer
from operators.operator import Operator


MOSES_PREPROCESS = {
    'en': [MosesPunctuationNormalizer('en'), MosesTokenizer('en')],
    'fr': [MosesPunctuationNormalizer('fr'), MosesTokenizer('fr')],
}


class MosesTokenize(Operator):
    def preprocess(self, text, lang='en'):
        punct, tokenizer = MOSES_PREPROCESS[lang]
        s = punct(text)
        if isinstance(s, str):
            return ' '.join(tokenizer(s)), {'raw': text}
        else:
            return '', {'raw': text}
    
    def postprocess(self, text_tgt_matched, mapping_tgt_matched, lang, mapping_src_ref):
        return text_tgt_matched
