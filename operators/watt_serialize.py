import utils
from operators.operator import Operator




class WattSerialize(Operator):
    def preprocess(self, text, lang='en'):
        return utils.serialize(text)

    __DIRECTIONS = {'en': 'f2e', 'fr': 'e2f'}

    def postprocess(self, text_tgt_matched, mapping_tgt_matched, lang, mapping_src_ref):
        mapping_tgt = utils.translate_mapping(mapping_tgt_matched, mapping_src_ref, self.__DIRECTIONS[lang])
        return utils.deserialize(text_tgt_matched, mapping_tgt)

