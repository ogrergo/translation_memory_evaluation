from backend import MySQLBackend
from sentence import Sentence


class MySQLOneWordBackend(MySQLBackend):

    @staticmethod
    def split_one_word_hash(sentence):
        res = []
        for i, _ in enumerate(sentence.key.split(' ')):
            res.append(' '.join(sentence.key[:i] + sentence.key[i+1:]))
        return res

    def add(self, sentence_src, sentence_tgt):
        c = self.connection.cursor()
        self._do_add(c, sentence_src, sentence_tgt)
        self.connection.commit()

    def find(self, sentence):
        with self.connection.cursor() as c:
            c.execute("""SELECT TU_tgt.mapping 
                               FROM (
                                        SELECT translations.id_{} as id
                                        FROM translations_units 
                                        INNER JOIN translations 
                                        ON translations.id_{} = translations_units.id AND
                                           translations_units.text_hash IN {} AND translations_units.language = {}
                                    ) as trans                         
                               INNER JOIN translations_units as TU_tgt 
                               ON trans.id = TU_tgt.id
                               ORDER BY TU_tgt.id DESC""".format('en' if sentence.language == 'fr' else 'fr',
                                                                 sentence.language, self.C, self.C),
                            ([self.hash(s) for s in self.split_one_word_hash(sentence)], sentence.language))

            return [Sentence.deserialize(t['mapping']) for t in c.fetchall()]

