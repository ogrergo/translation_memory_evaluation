import random

DIRECTIONS = ['random', 'en2fr', 'fr2en']


class Dataset:
    def __init__(self, fr_file, en_file, name, direction='random', max_line=None):
        self.fr_file = fr_file
        self.en_file = en_file
        self.name = name

        self.max_line = max_line

        assert direction in DIRECTIONS
        self.direction = direction

    def __iter__(self):
        with open(self.fr_file) as fp_fr, open(self.en_file) as fp_en:
            for i, (line_fr, line_en) in enumerate(zip(fp_fr, fp_en)):
                if self.max_line and i > self.max_line:
                    break
                line_fr = line_fr.strip()
                line_en = line_en.strip()

                yield self._apply_direction(line_fr, line_en)

    def iter_operator(self, operator):
        for l_src, l_tgt, direction in self:
            yield operator.preprocess(l_src, direction[:2]), operator.preprocess(l_tgt, direction[3:]), direction

    def _apply_direction(self, line_fr, line_en):
        direction = self.direction
        if direction == 'random':
            direction = random.choice(['en2fr', 'fr2en'])

        if direction == 'en2fr':
            return line_en, line_fr, direction
        else:
            return line_fr, line_en, direction