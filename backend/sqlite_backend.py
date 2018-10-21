import hashlib

from tqdm import tqdm
from sentence import Sentence
from backend.backend import Backend
import sqlite3
import os


class SQLBackend(Backend):

    C = '?'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection = None

    def find(self, sentence):
        with self.connection.cursor() as c:
            c.execute("""SELECT TU_tgt.mapping 
                               FROM (
                                        SELECT translations.id_{} as id
                                        FROM translations_units 
                                        INNER JOIN translations 
                                        ON translations.id_{} = translations_units.id AND
                                           translations_units.text_hash = {} AND translations_units.language = {}
                                    ) as trans                         
                               INNER JOIN translations_units as TU_tgt 
                               ON trans.id = TU_tgt.id
                               ORDER BY TU_tgt.id DESC""".format('en' if sentence.language == 'fr' else 'fr',
                                                                 sentence.language, self.C, self.C),
                            (self.hash(sentence.key), sentence.language))

            return [Sentence.deserialize(t['mapping']) for t in c.fetchall()]

    def add(self, sentence_src, sentence_tgt):
        c = self.connection.cursor()
        self._do_add(c, sentence_src, sentence_tgt)
        self.connection.commit()

    def load(self, dataset):
        self.connection = self._open_connection()
        self._clear_tables()

        with self.connection.cursor() as c:
            for sentence_src, sentence_tgt in tqdm(dataset.iter_operators(), "Populating TM {} :".format(dataset.name)):
                self._do_add(c, sentence_src, sentence_tgt)

        self.connection.commit()

    def _do_add(self, cursor, sentence_src, sentence_tgt):
        assert sentence_src.language != sentence_tgt.language

        cursor.execute("INSERT IGNORE INTO translations_units(language, text, text_hash, mapping) VALUES({},{},{},{}) ".format(self.C, self.C, self.C, self.C,),
                  (sentence_src.language, sentence_src.key, self.hash(sentence_src.key), Sentence.serialize(sentence_src)))

        src_id = cursor.lastrowid

        cursor.execute("INSERT IGNORE INTO translations_units(language, text, text_hash, mapping) VALUES({},{},{},{}) ".format(self.C, self.C, self.C, self.C),
                  (sentence_tgt.language, sentence_tgt.key, self.hash(sentence_src.key), Sentence.serialize(sentence_tgt)))

        tgt_id = cursor.lastrowid

        if sentence_src.language == 'fr':
            id_fr = src_id
            id_en = tgt_id
        else:
            id_fr = tgt_id
            id_en = src_id

        cursor.execute("INSERT IGNORE INTO translations(id_fr, id_en) VALUES({},{}) ".format(self.C, self.C,),
                  (id_fr, id_en))

    def _open_connection(self):
        return sqlite3.connect(os.path.join(self.parameters['folder'], 'TM.db'))

    def _clear_tables(self):
        with self.connection.cursor() as c:
            c.execute("DROP TABLE IF EXISTS translations")
            c.execute("DROP TABLE IF EXISTS translations_units")

            c.execute('''CREATE TABLE translations_units (
                id        INTEGER PRIMARY KEY , 
                language  CHAR(2) NOT NULL,
                text_hash CHAR(64) NOT NULL,
                text      TEXT NOT NULL, 
                mapping   TEXT NOT NULL
            )''')

            c.execute("CREATE UNIQUE INDEX index_translations_units ON translations_units (language, text_hash);")

            c.execute('''CREATE TABLE translations (
                id      INTEGER PRIMARY KEY , 

                id_fr   INTEGER NOT NULL,
                id_en   INTEGER NOT NULL,
                
                FOREIGN KEY(id_fr) REFERENCES translations_units(id), 
                FOREIGN KEY(id_en) REFERENCES translations_units(id)
            )''')
            c.execute("CREATE UNIQUE INDEX index_translations ON translations (id_fr, id_en);")

        self.connection.commit()

    @staticmethod
    def hash(t):
        return hashlib.sha256(t.encode('utf8')).hexdigest()[:64]