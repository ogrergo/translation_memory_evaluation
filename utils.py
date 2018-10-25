# import MetServer
import re
from collections import defaultdict
from itertools import count

from nltk.translate.bleu_score import corpus_bleu
import nltk
from googletrans import Translator
import unidecode

translator = Translator()



def count_lines(f):
    with open(f) as fp:
        i = -1
        for i, _ in enumerate(fp):
            pass
        return i + 1

REPLACE_PATTERN = [
#    (r"(^|\.)[.\s]*\d{1,2}(:|h)\d\d\s((p|a)\.m|(P|A)M)\s*(?=\.)", ''), # sentence with hours in it
    (r"\.\s*\.", "."), # empty sentence,
    (r"[pP]\.?[mM]\.?", 'pm'),
    (r"[aA]\.?[mM]\.?", 'am'),

    # (r"\..(?=\s)", "."),
    (r"\.(\s*(?=[A-Z])|\s+(?=[\u00C0-\u00DC0-9a-z]))", " . \n") # sentence splitting
]
REPLACE_PATTERN = [(re.compile(p[0]), p[1]) for p in REPLACE_PATTERN]

def split_sentences(t):
    for p in REPLACE_PATTERN:
        t = re.sub(p[0], p[1], t)

    return t.split('\n')


REPLACE_PATTERN2 = [
    (r"\s{2,}", " "), # remove spaces
]

MATCH_TOKENS = [
    (r'\d+(:\d+)?\s[PA]\.?M\.?', 'TIME'),
    (r'\d+\s((TO|AND)\s\d+\s)?[CM]?M\b', 'HEIGHT'),
    (r'\d+\s((TO|AND)\s\d+\s)?KM\s/\sH', 'SPEED')
]

TOKENS_NAMES = {
    'TIME',
    'HEIGHT',
    'TEMPERATURE',
    'SPEED'
}


def tokenize2(sent):
    it = iter(count())
    tokens_value = {}

    def get_token(name, value):
        assert name in TOKENS_NAMES
        token = '_{}#{}'.format(name, next(it))
        tokens_value[token] = value
        return token

    sent = unidecode.unidecode(sent).upper()

    # remove double space
    for pattern, repl in REPLACE_PATTERN2:
        sent = sent.replace(pattern, repl)

    while True:
        for pattern, name in MATCH_TOKENS:
            matchs = list(re.finditer(pattern, sent))
            if matchs:
                pos = matchs[0].regs[0]
                sent = '{} {} {}'.format(sent[:pos[0]].strip(),
                                         get_token(name, sent[pos[0]:pos[1]]),
                                         sent[pos[1]:].strip())
                break
        else:
            break

    return sent


NUMBER_REGEXP = r'((?<!\S)|^)[+-]?\d+([.,]\d+)?(?=([\s.]|$))'
EMAIL_REGEXP = r'((?<!\S)|^)([A-Z]{2,}.){1,3}[A-Z]{2,}@([A-Z]{2,}.){1,3}[A-Z]{2,}(?=([\s.]|$))'




MONTH_ABBREVS_MAP_EN = { "JAN" : "JANUARY", 'FEB' : 'FEBRUARY' , 'MAR' : 'MARCH',
                     'APR' : 'APRIL', 'MAY' : 'MAY', 'JUN' : 'JUNE', 'JUL' : 'JULY',
                     'AUG' : 'AUGUST', 'SEP' : 'SEPTEMBER', 'SEPT' : 'SEPTEMBER',
                     'OCT' : 'OCTOBER', 'NOV' : 'NOVEMBER', 'DEC' : 'DECEMBER' }

MONTH_ABBREVS_EN = list(MONTH_ABBREVS_MAP_EN.keys())

TAF_ADAPTER_EN = [ # attempts to adapt taf notes to weather report language...
                  (r'(\d)°', r'\1 ° '), # space degree from number
                  (r'([<>~])(\d)', r'\1 \2'), # less-than, morethan, roughly
                  (r'!+', ' . '), # new punctuation
                  (r'\?', ' ? '), # new punctuation
                  # (r':', ' : '), # colon - doesn't work because of timestamps
                  (r'"', r' " '), # separate double quotes
                  (r'\*', r' '), # remove emphasis *
                  (r'([^-])--([^-])', r'\1 - \2'), # long dash
                  ]

# as used in our corpora, may be a problem when at the
# end of a sentence, i.e. IN B.C. -> IN BRITISH COLUMBIA (without period)
PROVINCE_NORMALIZER = [
                  # In French
                  (r'\bTNO\b', r'TERRITOIRES DU NORD-OUEST'),
                  (r'\bT\.?-N\.?-O\.?', r'TERRITOIRES DU NORD-OUEST'),
                  (r'\bC\.?-B\.?', r'COLOMBIE-BRITANNIQUE'),
                  (r'\bI\.P\.E\.', r'ILE-DU-PRINCE-EDOUARD'),
                  (r'\bE\.-U\.', r'ETATS-UNIS'),
                  # In English
                  (r'\bNWT\b', r'NORTHWEST TERRITORIES'),
                  (r'\bSK\b', r'SASKATCHEWAN'),
                  (r'\bB\.C\.', r'BRITISH COLUMBIA'),
                  (r'\bP\.E\.I\.', r'PRINCE EDWARD ISLAND'),
                  (r'\bU\.S\.', r'UNITED STATES'),
                ]

# SPLIT_TOKENIZERS acts as both a normalizer and a tokenizer
SPLIT_TOKENIZERS =  TAF_ADAPTER_EN + \
                    PROVINCE_NORMALIZER + \
                    [
                    (r'^ *\.* *', r''), # remove leading periods
                    (r'^ *"* *', r''), # remove leading quotes jic
                    (r' *"* *$', r''), # remove trailing quotes jic
                    (r'^(>{1,2} *)?\d+>>', r''), # remove stray sentence indicators >>1>>, > 40>>
                    (r'([PA])\.M\. *$', r' \1M.'), # normalize PM and AM
                    (r'([PA])\.M\.', r' \1M'),
                    (r'\b(KNOTS|KNTS|KNOT|KT)\b', r'KN'), # normalize knots
                    (r'(\d)(KNOTS|KNTS|KNOT|KT)\b', r'\1 KN'),
                    (r'\bS\.V\.P\. *$', r'SVP.'), # normalize S.V.P.
                    (r'S\.V\.P\.', r'SVP'), # normalize S.V.P.
                    (r'CENTIM.TRES?', r'CM'), # normalize MM, KM and CM
                    (r'MILLIM.TRES?', r'MM'),
                    (r'KILOM.TRES?', r'KM'),
                    (r'\bM.TRES?', r' M'),
                    (r'(\d)([CKM]M)', r'\1 \2'), # space between unit and digit
                    # (r'\bPERCENT\b', r' %'), # percent
                    (r'(\d)%', r'\1 %'), # space between unit and %
                    (r"['`]", r' '), #remove all apostrophes - their rule
                    (r'(\d{1,2})[.:;]([0-5][0-9]) *(AM|PM)', r'\1:\2 \3 '), #normalize times
                    (r'(\d{1,2});([0-5][0-9]) *(AM|PM)', r'\1:\2 \3 '),
                    (r'={2,}', r''), # remove long separators like ========== or ----
                    (r'-{2,}', r''),
                    (r'([^.]|^)\.\.([^.]|^)', r'\1 , \2'), # .. -> ,  I'm not sure
                    (r'\.{4,}', r' , '), # long lines of ...... -> comma
                    (r'\.{2,4}', r' . '), # normalize .. and ... and ....;
                    (r'\.;', r'.'),
                    (r';', r'.'),
                    (r' *,([^\d]) *', r' , \1'), # split at commas when not followed by digit
                    (r'\(', r' ( '), # split at parentheses
                    (r'\)', r' ) '),
                    (r'(, *){2,}', ' , '), # replace multiple commas with only one
                    (r':([^\d])', r' : \1'), # split at colons when not followed by digit
                    (r'/', r' / '), # split all expressions sep. with a slash
                    (r'\bKM */ *HR?\b', r'KM/H'), # split KM/H
                    (r'\bC[\. ]?M\.?\b', r'CM'),
                    (r'\bM[\. ]?M\.?\b', r'MM'),
                    ]

SPLIT_REPLACES = [
                  (r'(?i)METEOROLOGIQUES *\.+ *ET LES', r'METEOROLOGIQUES ET LES'),
                  ('S.V.P. CONSULTER', 'VEUILLEZ CONSULTER'),
                  ('SVP CONSULTER', 'VEUILLEZ CONSULTER'),
                  (r'NICKEL SIZED', r'21 MM'), # TODO: complete this list
                  (r'NICKEL-SIZED', r'21 MM'),
                  (r'DIME SIZED', r'18 MM'),
                  (r'DIME-SIZED', r'18 MM'),
                  (r'QUARTER SIZED', r'24 MM'),
                  (r'QUARTER-SIZED', r'24 MM'),
                  (r'GOLF BALL SIZED?', r'45 MM'),
                  (r'GOLF-BALL SIZED?', r'45 MM'),
                  (r'\. +\.+ *VEUILLEZ ', r'. VEUILLEZ '),
                 ]
SPLIT_PROTECT = [ (r'STORM *\. *ONTARIO.*GC\. *CA', r'STORM.ONTARIO@EC.GC.CA'),
                  (r'TEMPETE *\. *ONTARIO.*GC\. *CA', r'TEMPETE.ONTARIO@EC.GC.CA'),
                  (r'\sST\.\s', r'ST.'), # saint
                  (r'\sFT\.\s', r'FT.'), # fort
                  (r'RAPPEL\.\.\.', r'RAPPEL...'),
                  (r'EX\. *:', r'EX. :'), # example
                  (r'E\.G\. *:', R'EX. :'),  ]
SPLIT_NOTOK = [r'(HTTP *: *// *)?WWW[A-Z0-9/\.-]*[A-Z0-9/]', # url with www, http optional
               r'HTTP *: *// *[A-Z0-9/\.-]*[A-Z0-9/]', # regular url, http mandatory
               NUMBER_REGEXP,
               EMAIL_REGEXP,
                ] + [m + r'\.' for m in MONTH_ABBREVS_EN if m != 'MAY']
NOT_BOUNDARY = {'-', '.', ':', '+', '*', '/', '!', '[', ']'} # removes some characters to regex class \b

DAYS_EN = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY","SUNDAY"]
DAYS_FR = ["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI","SAMEDI","DIMANCHE"]

MONTHS_EN = ["JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE","JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"]
MONTHS_FR = ["JANVIER","FEVRIER","MARS","AVRIL","MAI","JUIN","JUILLET","AOUT","SEPTEMBRE","OCTOBRE","NOVEMBRE","DECEMBRE"]

ALL_MONTHS = MONTHS_EN + MONTHS_FR
ALL_MONTHS.remove('MAY') # we remove the month of MAY, because it's also a verb



SERIALIZERS = [
    ("__DAY__", [r'\b{}\b'.format(m) for m in DAYS_EN + DAYS_FR]),
    ("__MONTH__", [r'\b{}\b'.format(m) for m in ALL_MONTHS]),

    ("__TIME__",
     [
         r'\b[0-2]?[0-9] *H( *[0-5][0-9])?\b',
         r'\b[0-2]?[0-9]([H;:.][0-5][0-9])? [AP]\.?M\.?\b',
         r'\b[0-2]?[0-9]:[0-5][0-9]\b',  # although incorrect wihout PM/AM
         # taf time (http://www.basair.com.au/index.php/online-resources/decoding-a-taf.html)
         r'\b\d+Z\b',
     ]),

    ("__REPORT__",
     [
         r'\bWWCN\d\d\b',
     ]),

    ("__NUM__",
     [
         # We want to capture 12-30, but not 1-800-888-8888, so we
         # use a negative lookahead and lookbehind expression.
         # See function serialize() for more info
         r'\b(?<!\S)\d+-\d+(?!\S)\b',
         NUMBER_REGEXP  # integer or fraction, possibly signed
     ]),
]

SERIALIZER_TOKNAMES = [x[0] for x in SERIALIZERS]


def tokenize(sent):
    """Tokenizes line in distinct sentences and words.
       Returns a list of lines.
       Will find sentence boundaries iff splitLine is True.
       Will always split at hard returns '\n'
       """

    if not sent or not sent.strip():
        return []

    # remove diacritics, recommended
    sent = unidecode.unidecode(sent)

    # ad hoc adjustments
    for pattern, repl in SPLIT_REPLACES:
        sent = re.sub(pattern, repl, sent, flags=re.I | re.A)

    # protect all entities not splittable (see also below)
    for i in range(0, len(SPLIT_PROTECT)):
        sent = re.sub(SPLIT_PROTECT[i][0], ' NOSPLITTOKEN' + str(i) + ' ', sent, flags=re.I | re.A)

    # 2nd flavor of split-protection
    allMatchObjects = []  # record all match objects, now
    for pattern in SPLIT_NOTOK:
        allMatchObjects += re.finditer(pattern, sent, flags=re.I | re.A)

    # sort in order of appearance
    allMatchObjects.sort(key=lambda matchObject: matchObject.start())
    # remove overlap (this should NOT happen, but problem with URL pattern, so...)
    # this is only a heuristic, and imperfect
    overlappingIndices = []
    for i in range(0, len(allMatchObjects) - 1):
        matchObject = allMatchObjects[i]
        nextMatchObject = allMatchObjects[i + 1]
        if matchObject.end() >= nextMatchObject.start():
            overlappingIndices += [i]

    for doomedIndex in reversed(overlappingIndices):
        del allMatchObjects[doomedIndex]

    # protect with token
    splitProtectedList = []
    protectionIndex = 0  # the index of the original string, in splitProtectedList
    newLine = ''
    lastIndex = 0
    for matchObject in allMatchObjects:  # scan match objects and replace in string
        newLine += sent[lastIndex:matchObject.start()]
        newLine += ' TOKPROTECTED' + str(protectionIndex) + ' '

        protectionIndex += 1
        lastIndex = matchObject.end()
        splitProtectedList.append(matchObject.group(0))

    newLine += sent[lastIndex:]
    sent = newLine

    # end of protection, now split and normalizes words
    for (pattern, repl) in SPLIT_TOKENIZERS:
        sent = re.sub(pattern, repl, sent, 0, flags=re.I | re.A)
        # print pattern, line, # debug

    replPatternForPeriod = r' . \n'
    sent = re.sub(r' *\. *', replPatternForPeriod, sent, flags=re.I | re.A)

    lineList = sent.split('\n')  # we always split

    # restore protected entities (from SPLIT_NOTOK)
    pattern = re.compile(r'TOKPROTECTED(\d+)', flags=re.I | re.A)
    for i in range(len(lineList)):
        sent = lineList[i]
        matchObj = pattern.search(sent)
        while matchObj:
            replacement = splitProtectedList[int(matchObj.group(1))]
            sent = sent[0:matchObj.start()] + replacement + \
                   sent[matchObj.end():]
            matchObj = pattern.search(sent)

        lineList[i] = sent

    # restore protected entities - some code duplication, here
    pattern = re.compile(r'NOSPLITTOKEN(\d+)', flags=re.I | re.A)
    for i in range(len(lineList)):
        sent = lineList[i]
        matchObj = pattern.search(sent)
        while matchObj:
            replacement = SPLIT_PROTECT[int(matchObj.group(1))][1]
            sent = sent[0:matchObj.start()] + replacement + \
                   sent[matchObj.end():]
            matchObj = pattern.search(sent)

        lineList[i] = sent

    # normalize space
    tokenized = [' '.join(l.strip().split()) for l in lineList if l.strip()]

    # if len(tokenized) != 1:
    #     raise ValueError("Invalid tokenization, multiple or no sentence on \"{}\"".format(tokenized))

    return tokenized


# def serialize(sent):
#     text, mapping = MetServer.serialize(sent)
#     return text, mapping


_translation_cache = {}


def translate(sent, src_lang):
    dest = 'en' if src_lang == 'fr' else 'fr'
    src = 'en' if src_lang == 'en' else 'fr'

    if sent not in _translation_cache:
        translation = translator.translate(sent, dest=dest, src=src).text
        _translation_cache[sent] = translation
    else:
        print("hit !")


    return _translation_cache[sent]


def bleu(candidates, references):
    candidates = [nltk.word_tokenize(sent) for sent in candidates]
    references = [[nltk.word_tokenize(sent)] for sent in references]

    return corpus_bleu(references, candidates)


def count_lines(file):
    with open(file) as fp:
        i = 0
        for i, l in enumerate(fp):
            pass

        return i

def serialize(sent):
    """Serializes a sentence, replacing specific patterns by
       serialization tokens, like __TIME__ or __MONTH__

       Returns the serialized sentence as well as a map describing what
       serializations took place. The format of the map is as follows:

       {__TOKENNAME__ : [ ("NON SERIALIZED SRC STRING", srcstartpos, srcendpos ) ]}

       where
       __TOKENNAME__ is the serialized token name, like __MONTH__
       "NON SERIALIZED SRC STRING" is, for ex., "OCTOBER", or "3 AM"
       (srcstartpost, srcendpos) is the range of positions (in token offset)
                                 where the src string was found. Boundaries
                                 are included in the range. The positions are
                                 in the serialized sentence, not in the
                                 original one, and account for possible token
                                 suppressions.

       the list associated with each tokenname is guaranteed to be in order of
       occurrence in the source sentence
    """
    # this set hold all the indexes of character replaced in the sentence
    positions = {}

    for tokenName, patternList in SERIALIZERS:
        for p in patternList:
            for m in re.finditer(p, sent, re.I | re.A):
                pos = m.regs[0]
                positions[pos] = (tokenName, sent[pos[0]: pos[1]])

    res = defaultdict(list)
    indexes = []
    for k, v in positions.items():
        res[v[0]].append((v[1], *k))
        indexes.append((*k, v[0]))

    res_sent = ''
    last = 0
    for s, e, tok in sorted(indexes):
        res_sent += sent[last:s]
        res_sent += tok
        last = e

    res_sent += sent[last:len(sent)]

    return res_sent, dict(res)

def serialize_from_dict(sent, dicts, lang):

    positions = {}
    curr = 0

    for w in sent.split(' '):
        for d in dicts:
            if w in dicts[d][lang]:
                positions[(curr, len(w) + curr)] = (d, w)
            curr += len(w) + 1

    res = defaultdict(list)
    indexes = []
    for k, v in positions.items():
        res[v[0]].append((v[1], *k))
        indexes.append((*k, v[0]))

    res_sent = ''
    last = 0
    for s, e, tok in sorted(indexes):
        res_sent += sent[last:s]
        res_sent += tok
        last = e

    res_sent += sent[last:len(sent)]

    return res_sent, dict(res)


def deserialize(sent, tok_map):
    for tok, v in tok_map.items():
        for r in sorted((*t[1:3], t[0]) for t in v):
            sent = re.sub(tok, r[2], sent, count=1)

    return sent



_TRANSLATE_TOKEN_e2f = {
    **{e.lower(): f.lower() for e, f in zip(MONTHS_EN, MONTHS_FR)},
    **{e.lower(): f.lower() for e, f in zip(DAYS_EN, DAYS_FR)},
}

_TRANSLATE_TOKEN_f2e = {v:e for e,v in _TRANSLATE_TOKEN_e2f.items()}
assert len(_TRANSLATE_TOKEN_e2f) == len(_TRANSLATE_TOKEN_f2e)

def _translate_token(token, value, direction):
    if direction == 'f2e':
        trans = _TRANSLATE_TOKEN_f2e
        up_case = True
    else:
        trans = _TRANSLATE_TOKEN_e2f
        up_case = False

    if token in {'__MONTH__', '__DAY__'}:
        try:
            value = trans[value.lower()]
        except KeyError:
            value = value.lower()

        if up_case: value = value.capitalize()

    return value


def translate_mapping(mapping_src, mapping_tgt, direction):
    if set(mapping_src,) ^ set(mapping_tgt):
        print('Invalid mapping couples -different tokens')
        return {}

    res = defaultdict(list)
    for k in mapping_src:
        if len(mapping_src[k]) != len(mapping_tgt[k]):
            print("Invalid mapping couples -different length")
            continue

        for e_src, e_tgt in zip(mapping_src[k], mapping_tgt[k]):
            value, _, _ = e_src
            _, c0, c1 = e_tgt
            res[k].append((_translate_token(k, value, direction), c0, c1))

    return dict(res)


def _translate_token_dict(token, value, direction, dict):
    if direction == 'f2e':
        trans = dict[token]['fr']
    else:
        trans = dict[token]['en']

    return trans[value.lower()]


def translate_mapping_dict(mapping_src, mapping_tgt, direction, dicts):
    if set(mapping_src,) ^ set(mapping_tgt):
        raise ValueError('Invalid mapping couples')

    res = defaultdict(list)

    for k in mapping_src:
        if len(mapping_src[k]) != len(mapping_tgt[k]):
            raise ValueError('Invalid mapping couples')

        for e_src, e_tgt in zip(mapping_src[k], mapping_tgt[k]):
            value, _, _ = e_src
            _, c0, c1 = e_tgt
            res[k].append((_translate_token_dict(k, value, direction, dicts), c0, c1))

    return dict(res)

from _sha256 import sha224


def hash_text(text):
    return sha224(text.encode('utf8')).hexdigest()


def iter_drop_token(s):
    # return a iterable of sentence missing a word. Return num words sentences
    ss = s.split()
    for i in range(len(ss)):
        yield ' '.join(ss[0:i] + ss[i + 1:len(ss)])

if __name__ == '__main__':
    _fr = "On prévoit des accumulations supplémentaires de 10 à 30 cm de neige d'ici lundi matin, et une accumulation plus importante est possible dans certains secteurs bien précis ."
    _en = "Additional snowfall amounts of 10 to 20 cm are expected by monday morning with the highest amounts likely to be quite localized ."

    # fr_serial, fr_mapping = serialize(_fr)
    # en_serial, en_mapping = serialize(_en)
    #
    # mapping_tgt = translate_mapping( en_mapping, fr_mapping, 'e2f')
    # print(deserialize(fr_serial, mapping_tgt))

    #

    dicts = {
        '__days': {'fr': {'lundi': 'monday'}, 'en': {'monday': 'lundi'}}
    }
    fr_serial, fr_mapping = serialize_from_dict(_fr, dicts, lang='fr')
    en_serial, en_mapping = serialize_from_dict(_en, dicts, lang='en')
    mapping_tgt = translate_mapping_dict(en_mapping, fr_mapping, 'e2f', dicts)
    res = deserialize(fr_serial, mapping_tgt)
    print(res)
