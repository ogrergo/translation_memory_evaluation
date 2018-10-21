from operators.operator import Operator
import utils


class WattTokenize(Operator):
    def preprocess(self, text, lang='en'):
        tok = utils.tokenize(text)
        if tok:
            return tok[0], {'raw': text}
        else:
            return text, {'raw': text}
    
    def postprocess(self, text_tgt_matched, mapping_tgt_matched, lang, mapping_src_ref):
        return text_tgt_matched
