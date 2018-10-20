import json
import utils
from tqdm import tqdm
import os
import shutil

class Simulator:
    def __init__(self, root, backend, operator, multimatcher, dataset_init, dataset_test):
        self.root = root
        self.name = "backend.{}_operator.{}_multimatch.{}_initialization.{}_testset.{}_direction.{}" \
                .format(backend.__name__,
                        operator.__name__,
                        multimatcher.__name__,
                        dataset_init.name,
                        dataset_test.name,
                        dataset_test.direction)

        self.folder = os.path.join(self.root, self.name)
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder)

        self.backend = backend({'folder': self.folder})
        self.operator = operator()
        self.multimatcher = multimatcher
        self.dataset_init = dataset_init
        self.dataset_test = dataset_test

    def run(self):
        self.backend.load(self.dataset_init, self.operator)

        matchs = self._pass_test_set()

        scores = self.compute_score(matchs)

        self.save_simulation(matchs, scores)

    def _pass_test_set(self):
        matchs = []
        for i, (test_src, test_tgt, direction) in enumerate(tqdm(self.dataset_test, 'Running simulation')):
            test_src_pre, test_src_map = self.operator.preprocess(test_src, lang=direction[:2])

            matched_many_pre = self.backend.find(test_src_pre, lang=direction[:2])
            if not matched_many_pre:
                matchs.append((direction, test_src, test_src_pre, test_src_map, test_tgt))
                continue

            matched_many_post = [self.operator.postprocess(*e, lang=direction[3:], mapping_tgt=test_src_map)
                                 for e in matched_many_pre]

            idx = self.multimatcher(matched_many_post, test_tgt)

            self.backend.add(test_src_pre, test_src_map,
                             *self.operator.preprocess(test_tgt, lang=direction[3:]),
                             direction, i)

            matchs.append((direction, test_src, test_src_pre, test_src_map, test_tgt,
                           len(matched_many_post), matched_many_post[idx], *matched_many_pre[idx]))

        return matchs

    def compute_score(self, matchs):
        bleu_oracle = []
        bleu_matched = []
        for match in tqdm(matchs, 'Computing TM scores'):
            if len(match) > 5:
                direction, test_src, test_src_pre, test_src_map, test_tgt, nb_matched, \
                match_post, match_pre, match_pre_map = match

                bleu_matched.append(utils.bleu([test_tgt], [match_post]))

        total = len(matchs)
        multi_matched = sum(1 if len(e) > 5 and e[5] > 1 else 0 for e in matchs)
        _matched = [len(e) > 5 for e in matchs]

        return {
            'bleu_total': sum(bleu_matched) / total,
            'bleu_matched': sum(bleu_matched) / len(bleu_matched),

            'nb_matched': sum(_matched),
            'ratio_matched': sum(_matched) / total,

            'nb_multi_matched': multi_matched,
            'ratio_multimatched': multi_matched / total,

            'nb_no_matched': sum(1 if not e else 0 for e in _matched),
            'ratio_no_matched': sum(1 if not e else 0 for e in _matched) / total,

            'total': total,
        }

    def save_simulation(self, matchs, scores):
        matched_file = os.path.join(self.folder, 'matched')
        not_matched_file = os.path.join(self.folder, 'not-matched')

        with open(matched_file, 'w') as fp_matched, open(not_matched_file, 'w') as fp_not_matched:
            for i, m in enumerate(matchs):
                if len(m) == 5:
                    direction, test_src, test_src_pre, test_src_map, test_tgt = m
                    fp_not_matched.write("{},{}#{}:[{}|{}->(nb:{})]|{}\n".format(
                        i,
                        direction,
                        test_src,
                        test_src_pre,
                        json.dumps(test_src_map),
                        0,
                        test_tgt
                    ))
                else:
                    direction, test_src, test_src_pre, test_src_map, test_tgt, nb_matched, \
                               match_post, match_pre, match_pre_map = m

                    fp_matched.write("{},{}#{}:[{}|{}->(nb:{}){}:{}]|{}\n".format(
                        i,
                        direction,
                        test_src,
                        test_src_pre,
                        json.dumps(test_src_map),
                        nb_matched,
                        match_pre,
                        match_post,
                        test_tgt
                    ))

        score_file = os.path.join(self.folder, 'scores')
        with open(score_file, 'w') as fp:
            json.dump(scores, fp=fp, indent=True)





