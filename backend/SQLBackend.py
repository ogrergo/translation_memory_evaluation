from tqdm import tqdm

from TM2.backend.backend import Backend
import sqlite3
import os
import json


class SQLBackend(Backend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 'folder' in self.params

        self.database_path = os.path.join(self.params['folder'], 'TM.db')
        self.connection = self._init_db()

    def find(self, text, lang):
        assert lang in ('en', 'fr')

        c = self.connection.cursor()

        res = c.execute("""SELECT TU_tgt.text, TU_tgt.mapping 
                           FROM (
                                    SELECT translations.id_{} as id
                                    FROM translations_units 
                                    INNER JOIN translations 
                                    ON translations.id_{} = translations_units.id AND
                                       translations_units.text = ? AND translations_units.language = ?
                                ) as trans                         
                           INNER JOIN translations_units as TU_tgt 
                           ON trans.id = TU_tgt.id
                           ORDER BY TU_tgt.id DESC""".format('en' if lang == 'fr' else 'fr', lang),
                        (text, lang))
        return [(text, json.loads(mapping)) for text, mapping in res]

    def add(self, text_src, mapping_src, text_tgt, mapping_tgt, direction, id):
        assert direction in ('en2fr', 'fr2en'), "Invalid direction '{}'".format(direction)

        c = self.connection.cursor()
        self._do_add(c, text_src, mapping_src, text_tgt, mapping_tgt, direction)
        self.connection.commit()

    def load(self, dataset, operator):
        c = self.connection.cursor()

        for (text_src, mapping_src), (text_tgt, mapping_tgt), direction in tqdm(dataset.iter_operator(operator),
                                                                                "Populating TM"):
            self._do_add(c, text_src, mapping_src, text_tgt, mapping_tgt, direction)

        self.connection.commit()

    def _do_add(self, cursor, text_src, mapping_src, text_tgt, mapping_tgt, direction):
        cursor.execute("INSERT INTO translations_units(language, text, mapping) VALUES(?,?,?) ",
                  (direction[:2], text_src, json.dumps(mapping_src)))

        src_id = cursor.lastrowid

        cursor.execute("INSERT INTO translations_units(language, text, mapping) VALUES(?,?,?) ",
                  (direction[3:], text_tgt, json.dumps(mapping_tgt)))

        tgt_id = cursor.lastrowid

        if direction[:2] == 'fr':
            id_fr = src_id
            id_en = tgt_id
        else:
            id_fr = tgt_id
            id_en = src_id

        cursor.execute("INSERT INTO translations(id_fr, id_en) VALUES(?,?) ",
                  (id_fr, id_en))

    def _init_db(self):
        connection = sqlite3.connect(self.database_path)
        c = connection.cursor()

        c.execute("DROP TABLE IF EXISTS translations")
        c.execute("DROP TABLE IF EXISTS translations_units")

        c.execute('''CREATE TABLE translations_units (
            id       INTEGER PRIMARY KEY AUTOINCREMENT, 
            language TEXT NOT NULL, 
            text     TEXT NOT NULL, 
            mapping  TEXT NOT NULL
        )''')

        c.execute("CREATE INDEX index_translations_units ON translations_units (language, text);")

        c.execute('''CREATE TABLE translations (
            id_fr   INTEGER NOT NULL,
            id_en   INTEGER NOT NULL,
            
            FOREIGN KEY(id_fr) REFERENCES translations_units(id), 
            FOREIGN KEY(id_en) REFERENCES translations_units(id)
        )''')

        connection.commit()

        return connection

if __name__ == '__main__':
    b = SQLBackend({'folder': '.'})

    b.add('dede', {}, 'deww', {}, 'en2fr', 0)
    b.add('dede', {}, 'de3ww', {}, 'en2fr', 0)
    print(b.find('dede', 'en'))
