import random as rd
from collections import Counter
import utils


def oracle(matched_many, target):
    return sorted(range(len(matched_many)), key=lambda i: -utils.bleu([matched_many[i]], [target]))[0]


def random(matched_many, target):
    return rd.randint(0, len(matched_many))


def lastseen(matched_many, target):
    return 0


def mostseen(matched_many, target):
    e = Counter(matched_many).most_common(1)[0][0]
    return [i for i, t in enumerate(matched_many) if t == e][0]
