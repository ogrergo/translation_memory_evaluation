import os
import traceback
from itertools import product
from multiprocessing import Queue, Process

# sys.path.append('/u/vanbeurl/code/scrap_warns')
import sys

from backend import MySQLBackend
from dataset import Dataset
from multimatch import oracle, random, mostseen
from operators import *
from operators import RemoveSpaces
from simulator import Simulator
from queue import Empty


def runnable(f):
    def wrapper(i, queue):
        while True:
            try:
                args = queue.get_nowait()
            except Empty:
                break

            name = "thread{} {}".format(i, args['run_name'])
            del args['run_name']

            print("{}: {}".format(f.__name__, name).capitalize(), file=sys.stderr)

            try:
                f(args)
            except Exception:
                print("!!! crashed : {}".format(name), file=sys.stderr)
                traceback.print_exc()

    return wrapper


def run_pool(task, args, N):
    q = Queue()
    process = [Process(target=task, args=(i, q)) for i in range(N)]

    for e in args:
        q.put(e)

    for p in process:
        p.start()

    for p in process:
        p.join()


@runnable
def build_dataset_cache(args):
    Dataset(**args).build_cache()


@runnable
def run_experiments(args):
    Simulator(**args).run()



def get_dataset_args(name, operators):
    return {'fr_file': os.path.join(DATA_ROOT, name + ".fr"),
            'en_file': os.path.join(DATA_ROOT, name + ".en"),
            'name': name,
            'operators': operators,
            'cache_root': CACHE_ROOT,
            'direction': 'random'}


if __name__ == '__main__':
    OPERATORS = [
        [],
        # [WattTokenize()],
        [WattSerialize(), LowerCase()],

        [WattSerialize()],

        [RemovePunct()],
        [RemoveSpaces()],
        [LowerCase()],
        [RemoveDiacritic()],

        # [RemoveSpaces(), RemovePunct(), LowerCase(), RemoveDiacritic()],
        #
        # # [WattSerialize(), RemoveSpaces(), RemovePunct(), LowerCase(), RemoveDiacritic()]
        #[MosesTokenize(), WattTokenize()],
        #[WattTokenize(), MosesTokenize()],
    ]

    DATA_ROOT = '/data/rali6/Tmp/vanbeurl/meteo-data'
    CACHE_ROOT = '/part/02/Tmp/experiments-meteo/TM_cache'
    # EXPERIMENT_FOLDER = '/data/rali6/Tmp/vanbeurl/meteo-data/TM_simulation/'
    EXPERIMENT_FOLDER = '/part/02/Tmp/experiments-meteo/TM_experiments'

    DATASETS_NAME = [
                    # 'sftp-clean.WattTokenize',
        #
        'empty.WattTokenize',
        'sftp-test-clean.WattTokenize',
        'watt-clean.WattTokenize',
        'portage-clean.WattTokenize',
                     ]
    # CACHE_ROOT = '/data/rali6/Tmp/vanbeurl/meteo-data/TM_cache'
    def _dt_name(init, operators):
        return "{}_{}".format(init, "+".join(op.name for op in operators))

    DATASETS_ARGS = [{'run_name': _dt_name(name, operators), **get_dataset_args(name, operators)} for name, operators in product(DATASETS_NAME, OPERATORS)]

    run_pool(build_dataset_cache, DATASETS_ARGS, 20)

    MULTIMATCHERS = [oracle, random, mostseen]

    def _name(init, operators, multimatcher):
        return "{}_{}_{}".format(init, "+".join(op.name for op in operators), multimatcher.__name__)

    EXPERIMENT_0 = [{
            'run_name': _name(init, operators, multimatcher),
            'exp_path': os.path.join(EXPERIMENT_FOLDER, _name(init, operators, multimatcher)),
            'backend': MySQLBackend({'host': '127.0.0.1', 'port': 3306, 'database': _name(init, operators, multimatcher)}),
            'multimatcher': multimatcher,
            'dataset_init': Dataset(**get_dataset_args(init, operators)),
            'dataset_test': Dataset(**get_dataset_args('sftp-test-clean.WattTokenize', operators))
        } for multimatcher,
              init,
              operators in product(
                MULTIMATCHERS,
                DATASETS_NAME,
                OPERATORS
    )]

    for e in EXPERIMENT_0:
        print("#Running {}".format(e['run_name']))
        del e['run_name']

        Simulator(**e).run()
    # run_pool(run_experiments, EXPERIMENT_0, 1)
