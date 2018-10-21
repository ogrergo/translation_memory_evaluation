import json


class Sentence:
    def __init__(self, text, language, line_number, dataset_name):
        self._transforms = [{
            'text': text,
            'mapping': {},
            'operator': 'raw',
            'parameters': {}
        }]

        self.dataset_name = dataset_name
        self.dataset_line = line_number
        self.language = language
    
    @property
    def key(self):
        return self._transforms[-1]['text']

    @property
    def source(self):
        return self._transforms[0]['text']
    
    def render_translation(self, sentence):
        res = self.key
        
        assert len(self._transforms) == len(sentence._transforms)
        from operators.operator import Operator

        for t, t_map in zip(reversed(self._transforms), reversed(sentence._transforms)):
            assert t['operator'] == t_map['operator'] and t['parameters'] == t_map['parameters']
            
            if t['operator'] == 'raw':
                break

            op = Operator.from_name(t['operator'], t['parameters'])
            res = op.postprocess(res, t['mapping'], self.language, t_map['mapping'])

        return res

    def apply_operator(self, operator):
        text, mapping = operator.preprocess(self.key, self.language)
        self._transforms.append({
            'text': text,
            'mapping': mapping,
            'operator': operator.name,
            'parameters': operator.parameters
            })
    
    def serialize(self):
        return json.dumps({
                '_transforms': self._transforms,
                'dataset_name': self.dataset_name,
                'line_number': self.dataset_line,
                'language': self.language
            })

    @staticmethod
    def deserialize(line):
        d = json.loads(line)
        s = Sentence(text=None, 
                     language=d['language'], 
                     line_number=d['line_number'], 
                     dataset_name=d['dataset_name'])

        s._transforms = d['_transforms']
        return s
        

