from TM2.backend.SQLBackend import SQLBackend
from TM2.config import EXPERIMENT_FOLDER
from TM2.dataset import Dataset
from TM2.multimatch import oracle
from TM2.operators.raw import Raw
from TM2.simulator import Simulator

if __name__ == '__main__':
    d = Dataset('/data/rali6/Tmp/vanbeurl/meteo-data/sftp.fr',
                '/data/rali6/Tmp/vanbeurl/meteo-data/sftp.en',
                'sftp')
    d_test = Dataset('/data/rali6/Tmp/vanbeurl/meteo-data/sftp-test.fr',
                '/data/rali6/Tmp/vanbeurl/meteo-data/sftp-test.en',
                'sftp-test')

    s = Simulator(
        root=EXPERIMENT_FOLDER,
        backend=SQLBackend,
        operator=Raw,
        multimatcher=oracle,
        dataset_init=d,
        dataset_test=d_test
    )
    s.run()

