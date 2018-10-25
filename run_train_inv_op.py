import os
from postprocessing.prepare_data import init_dataset

import os


DATA_ROOT = '/data/rali6/Tmp/vanbeurl/meteo-data'
CACHE_ROOT = '/part/02/Tmp/experiments-meteo/TM_cache'
EXPERIMENT_FOLDER = '/part/02/Tmp/experiments-meteo/TM_postprocess'

IN_SENTS = os.path.join(CACHE_ROOT, 'portage-clean.WattTokenize.RemovePunct.RemoveSpaces.')
OUT_SENTS = os.path.join(EXPERIMENT_FOLDER, 'portage-clean.WattTokenize.RemovePunct.RemoveSpaces.')

IN_TEST = os.path.join(CACHE_ROOT, 'sftp-test-clean.WattTokenize.RemovePunct.RemoveSpaces.')
OUT_TEST = os.path.join(EXPERIMENT_FOLDER, 'sftp-test-clean.WattTokenize.RemovePunct.RemoveSpaces.')




if __name__ == '__main__':
    init_dataset(IN_TEST + 'en', IN_TEST + 'fr',
                 OUT_TEST + 'en', OUT_TEST + 'fr')

    init_dataset(IN_SENTS + 'en', IN_SENTS + 'fr',
                 OUT_SENTS + 'en', OUT_SENTS + 'fr')

