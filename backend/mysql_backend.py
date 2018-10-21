import os
from itertools import count
from tempfile import mkstemp

import pymysql
from h5py.h5t import defaultdict
from tqdm import tqdm

from backend.sqlite_backend import SQLBackend
from sentence import Sentence


class MySQLBackend(SQLBackend):

    C = '%s'

    def load(self, dataset):
        tu_file, rel_file = self.write_data_infile(dataset)

        self.connection = self._open_connection()
        self._clear_tables()

        with self.connection.cursor() as c:
            c.execute("""LOAD DATA INFILE %s INTO TABLE translations_units 
            FIELDS TERMINATED BY '$$'
            LINES TERMINATED BY '\n'
            (id, language, text, text_hash, mapping)
            """, tu_file)
            c.execute("""LOAD DATA INFILE %s INTO TABLE translations 
                        FIELDS TERMINATED BY '$$'
                        LINES TERMINATED BY '\n'
                        (id, id_fr, id_en)
                        """, rel_file)

        self.connection.commit()

    def _open_connection(self):
        connection = pymysql.connect(host=self.parameters['host'],
                                     port=self.parameters['port'],
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        name = self.parameters['database']
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES", )

            for r in cursor.fetchall():
                if r['Database'] == name:
                    print(cursor.execute('DROP DATABASE `{}`'.format(name)))

            cursor.execute('CREATE DATABASE `{}`'.format(name))
            cursor.execute('USE `{}`'.format(name))

        connection.commit()

        return connection

    @staticmethod
    def write_data_infile(dataset):
        tu = defaultdict(iter(count()).__next__)
        rel = defaultdict(iter(count()).__next__)

        osfp_tu, data_infile_tu = mkstemp()
        osfp_rel, data_infile_rel = mkstemp()

        with os.fdopen(osfp_tu, 'w') as fp_tu, os.fdopen(osfp_rel, 'w') as fp_rel:
            for sentence_src, sentence_tgt in tqdm(dataset.iter_operators(), "Populating TM {} :".format(dataset.name)):
                k_src = (sentence_src.language, sentence_src.key)
                if k_src not in tu:
                    fp_tu.write('$$'.join([str(tu[k_src]), sentence_src.language, sentence_src.key, MySQLBackend.hash(sentence_src.key),
                                           Sentence.serialize(sentence_src)]) + '\n')
                idx_src = tu[k_src]

                k_tgt = (sentence_tgt.language, sentence_tgt.key)
                if k_tgt not in tu:
                    fp_tu.write('$$'.join([str(tu[k_tgt]), sentence_tgt.language, sentence_tgt.key, MySQLBackend.hash(sentence_tgt.key),
                                           Sentence.serialize(sentence_tgt)]) + '\n')
                idx_tgt = tu[k_tgt]

                if sentence_src.language == 'en':
                    e = idx_src
                    idx_src = idx_tgt
                    idx_tgt = e

                k_rel = (idx_src, idx_tgt)
                if k_rel not in rel:
                    fp_rel.write('$$'.join([str(rel[k_rel]), str(idx_src), str(idx_tgt)]) + '\n')

        return data_infile_tu, data_infile_rel