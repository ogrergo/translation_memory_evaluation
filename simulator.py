import json
import utils
from tqdm import tqdm
import os
import shutil



class Simulator:
    def __init__(self, exp_path, backend, multimatcher, dataset_init, dataset_test):
        self.folder = exp_path
        self.name = os.path.basename(exp_path)

        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder)

        self.backend = backend
        self.multimatcher = multimatcher
        self.dataset_init = dataset_init
        self.dataset_test = dataset_test

    def run(self):
        self.backend.load(self.dataset_init)

        matchs = self._pass_test_set()

        self.save_simulation(matchs)

    def _pass_test_set(self):
        matchs = []
        for test_src, test_tgt in tqdm(self.dataset_test.iter_operators(), 'Running simulation {} :'.format(self.name)):
            matched_many = self.backend.find(test_src)
            self.backend.add(test_src, test_tgt)

            direction = "{}2{}".format(test_src.language, test_tgt.language)

            if not matched_many:
                matchs.append((test_src, test_tgt, direction))
                continue

            matched_many_post = [e.render_translation(test_src) for e in matched_many]
            
            idx = self.multimatcher(matched_many_post, test_tgt.source)

            matchs.append((test_src, test_tgt, direction, len(matched_many), matched_many[idx], matched_many_post[idx]))

        return matchs

    def compute_scores(self, matchs):
        bleu_matched = []
        nb_matched_all = []

        for match in matchs:
            if len(match) > 3:
                test_src, test_tgt, direction, nb_matched, matched, matched_rendered = match

                bleu_matched.append(utils.bleu([test_tgt.source], [matched_rendered]))
                nb_matched_all.append(nb_matched)

        total = len(matchs)
        multi_matched = sum(1 if len(e) > 3 and e[3] > 1 else 0 for e in matchs)
        _matched = [len(e) > 3 for e in matchs]

        return {
            'bleu_total': sum(bleu_matched) / total,
            'bleu_matched': sum(bleu_matched) / len(bleu_matched),

            'nb_entry_matched': sum(_matched),
            'avg_nb_entry_matched': sum(_matched) / total,

            'nb_entry_multi_matched': multi_matched,
            'avg_nb_entry_multi_matched': multi_matched / total,

            'nb_database_match': sum(nb_matched_all),
            'avg-matched_nb_database_match': sum(nb_matched_all) / sum(_matched),

            'nb_no_matched': sum(1 if not e else 0 for e in _matched),
            'avg_no_matched': sum(1 if not e else 0 for e in _matched) / total,

            'nb_bleu_1': sum(1 if d == 1.0 else 0 for d in bleu_matched),
            'avg-matched_nb_bleu_1':  sum(1 if d == 1.0 else 0 for d in bleu_matched) / sum(_matched),

            'nb_bleu_between_1_0.7': sum(1 if d < 1.0 and d > 0.7 else 0 for d in bleu_matched),
            'avg-matched_nb_bleu_between_1_0.7': sum(1 if d < 1.0 and d > 0.7 else 0 for d in bleu_matched) / sum(_matched),

            'nb_bleu_below_0.7': sum(1 if d < 0.7 else 0 for d in bleu_matched),
            'avg-matched_nb_bleu_below_0.7': sum(1 if d < 0.7 else 0 for d in bleu_matched) / sum(_matched),

            'total': total,
        }

    def save_simulation(self, matchs):

        matched_file = os.path.join(self.folder, 'matched')
        not_matched_file = os.path.join(self.folder, 'not-matched')

        with open(matched_file, 'w') as fp_matched, open(not_matched_file, 'w') as fp_not_matched:
            for i, m in enumerate(matchs):
                if len(m) == 3:
                    test_src, test_tgt, direction = m
                    fp_not_matched.write("{},{}#{}:[{}->(nb:{})]|{}\n".format(
                        i,
                        direction,
                        test_src.source,
                        test_src.key,
                        0,
                        test_tgt.source
                    ))
                else:
                    test_src, test_tgt, direction, nb_matched, matched, matched_rendered = m

                    fp_matched.write("{},{}#{}:[{}->(nb:{}){}:{}]|{}\n".format(
                        i,
                        direction,
                        test_src.source,
                        test_src.key,
                        nb_matched,
                        matched.key,
                        matched_rendered,
                        test_tgt.source
                    ))

        scores = self.compute_scores(matchs)

        score_file = os.path.join(self.folder, 'scores')
        with open(score_file, 'w') as fp:
            json.dump(scores, fp=fp, indent=True)




if __name__ == '__main__':
    from backend import MySQLBackend

    b = MySQLBackend({'host': '127.0.0.1', 'port': 3306, 'database': 'dfafa'})
