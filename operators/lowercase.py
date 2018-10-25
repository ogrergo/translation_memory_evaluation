from operators.operator import Operator
import re


class LowerCase(Operator):
    def preprocess(self, text, lang):
        return text.lower(), {'raw': text}

    def postprocess(self, text_tgt_matched, mapping_tgt_matched, lang, mapping_src_ref):
        return mapping_tgt_matched['raw']

