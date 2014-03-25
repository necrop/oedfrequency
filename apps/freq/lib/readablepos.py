
TERSE = {'NN': 'noun', 'JJ': 'adjective', 'VB': 'verb', 'RB': 'adverb',
         'NP': 'proper name'}
VERBOSE = {'NN': 'singular', 'NNS': 'plural', 'NP': 'proper name',
           'JJ': 'adjective', 'JJR': 'comparative', 'JJS': 'superlative',
           'RB': 'adverb', 'VB': 'infinitive', 'VBZ': '3rd-person present',
           'VBG': 'present participle', 'VBD': 'past',
           'VBN': 'past participle'}


def readable_pos(pos, verbose=True):
    """
    Given a PENN code for a part of speech, returns a human-readable
    description of the part of speech.
    """
    if verbose:
        try:
            return VERBOSE[pos]
        except KeyError:
            return pos
    else:
        try:
            return TERSE[pos]
        except KeyError:
            return pos
