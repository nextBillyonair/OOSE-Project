from .nouns import NOUNS, ANIMALS
from .adjectives import ADJECTIVES, POLITE_ADJECTIVES
import random

def random_noun():
    return random.choice(NOUNS).title()

def random_adjective():
    return random.choice(ADJECTIVES).title()

def random_namepair():
    return u"{} {}".format(random_adjective(), random_noun())
