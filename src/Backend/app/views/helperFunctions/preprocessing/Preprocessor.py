from app.views.helperFunctions.preprocessing import SpellChecker
import functools
import os

WORDS_TO_IGNORE = set(file(os.path.dirname(os.path.abspath(__file__)) + '/words_to_ignore.txt').read().split('\n'))

# functions = [removeStopWords, getKeywords, SpellChecker.spell_check]

def compose(*functions):
    def compose2(f, g):
        return lambda x: f(g(x))
    return functools.reduce(compose2, functions, lambda x: x)

def removeStopWords(words):
    words = filter(lambda x: x not in WORDS_TO_IGNORE, words)
    return words

def getKeywords(tags):

    otherKeywords = []
    for tag in tags:
        if tag != "":
            for word in tag.strip().split():
                otherKeywords.append(word)

    return otherKeywords

# preprocessor = compose(*functions)
