import random
import os
from tqdm import tqdm
from utils import count_lines
from operators import Operator
from sentence import Sentence

DIRECTIONS = ['random', 'en2fr', 'fr2en']



class Dataset:
    def __init__(self, fr_file, en_file, name, 
                       operators, cache_root=None,
                       direction='random', max_line=None):

        self.fr_file = fr_file
        self.en_file = en_file

        self.max_line = max_line
        
        assert isinstance(operators, list) and all(isinstance(e, Operator) for e in operators)
        self.operators = operators

        assert direction in DIRECTIONS
        self.direction = direction

        self.name = '.'.join([name, *[op.name for op in operators]])

        if not cache_root:
            cache_root = os.path.dirname(self.fr_file)
        self.cache_root = cache_root
        self.cache_fr = os.path.join(cache_root, "{}.fr".format(self.name))
        self.cache_en = os.path.join(cache_root, "{}.en".format(self.name))
        
    @property
    def cache_exists(self):
        return os.path.isfile(self.cache_fr) and os.path.isfile(self.cache_en) and (\
                (not self.max_line and count_lines(self.cache_fr) == count_lines(self.fr_file) and count_lines(self.cache_en) == count_lines(self.en_file)) or \
                (count_lines(self.cache_fr) == self.max_line and count_lines(self.cache_en) == self.max_line))

    def build_cache(self):
        if self.cache_exists:
            return

        with open(self.cache_fr, 'w') as fp_fr, open(self.cache_en, 'w') as fp_en:
            for fr, en in tqdm(self.iter_operators(apply_direction=False), "Building cache for {}...".format(self.name)):
                fp_fr.write("{}\n".format(fr.serialize()))
                fp_en.write("{}\n".format(en.serialize())) 
                
    def __iter__(self):
        with open(self.fr_file) as fp_fr, open(self.en_file) as fp_en:
            for i, (line_fr, line_en) in enumerate(zip(fp_fr, fp_en)):
                if self.max_line and i > self.max_line:
                    break
                
                fr = Sentence(line_fr.strip(), 'fr', i, self.name)
                en = Sentence(line_en.strip(), 'en', i, self.name)
               
                yield fr, en

    def iter_operators(self, apply_direction=True):
        if not self.cache_exists:
            for fr, en in self:
                self._apply_operators(fr)
                self._apply_operators(en)

                if apply_direction:
                    yield self._apply_direction(fr, en)
                else:
                    yield fr, en
        else:
            with open(self.cache_fr) as fp_fr, open(self.cache_en) as fp_en:
                for fr_l, en_l in zip(fp_fr, fp_en):
                    fr = Sentence.deserialize(fr_l)
                    en = Sentence.deserialize(en_l)

                    if apply_direction:
                        yield self._apply_direction(fr, en)
                    else:
                        yield fr, en

    def _apply_direction(self, line_fr, line_en):
        direction = self.direction
        if direction == 'random':
            direction = random.choice(['en2fr', 'fr2en'])

        if direction == 'en2fr':
            return line_en, line_fr
        else:
            return line_fr, line_en

    def _apply_operators(self, sentence):
        for op in self.operators:
            sentence.apply_operator(op)
