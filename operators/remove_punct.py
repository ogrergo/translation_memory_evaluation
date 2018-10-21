from operators.operator import Operator
import re


class RemovePunct(Operator):
    def preprocess(self, text, lang):
        return re.sub(r'[^a-zA-Z0-9\s]', '', text), {'raw': text}

    def postprocess(self, text_tgt_matched, mapping_tgt_matched, lang, mapping_src_ref):
        return mapping_tgt_matched['raw']

