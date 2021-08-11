__all__ = ['Preprocessor', 'SpellChecker']

from app.views.helperFunctions.preprocessing.Preprocessor import compose, removeStopWords, getKeywords
from app.views.helperFunctions.preprocessing import SpellChecker

functions = [removeStopWords, getKeywords, SpellChecker.spell_check]
preprocessor = compose(*functions)