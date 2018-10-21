class Operator:
    def __init__(self, parameters=None):
        self.parameters = parameters if parameters else {}
    
    @staticmethod
    def from_name(name, parameters):
        import operators
        op_class = operators.__dict__[name]

        return op_class(parameters)

    @property
    def name(self):
        return self.__class__.__name__

    def preprocess(self, text, lang):
        return text, {}

    def postprocess(self, text_tgt_matched, mapping_tgt_matched, lang, mapping_src_ref):
        return text_tgt_matched
