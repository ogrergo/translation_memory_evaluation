from operators.operator import Operator
import re
import unicodedata

def _remove_diacritics(txt):
    """This method removes all diacritic marks from the given string"""
    norm_txt = unicodedata.normalize('NFD', txt)
    shaved = ''.join(c for c in norm_txt if not unicodedata.combining(c))
    return unicodedata.normalize('NFC', shaved)


class RemoveDiacritic(Operator):
    def preprocess(self, text, lang):
        return _remove_diacritics(text), {'raw': text}

    def postprocess(self, text_tgt_matched, mapping_tgt_matched, lang, mapping_src_ref):
        return mapping_tgt_matched['raw']

