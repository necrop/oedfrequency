
sorts = (
    ('l', 'lemma order'),
    ('freqd', 'frequency (descending)'),
    ('freqa', 'frequency (ascending)'),
    ('increase', 'increase since 1800'),
    ('decrease', 'decrease since 1800'),
    ('fda', 'first date'),
    ('fdd', 'first date (reverse)'),
)

bands = (
    (1, '1 (highest)'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8 (lowest)'),
)

wordclasses = (
    ('any', 'any'),
    ('nn', 'noun'),
    ('jj', 'adjective'),
    ('vb', 'verb'),
    ('rb', 'adverb'),
    ('cc', 'conjunction'),
    ('in', 'preposition'),
    ('pp', 'pronoun'),
    ('uh', 'interjection'),
)

entrytypes = (
    ('any', 'any'),
    ('main', 'main entries only'),
    ('subentries', 'subentries only'),
)


class SearchForm(object):

    def __init__(self, store):
        self.store = store

    def lemma(self):
        return self.store.get('lemma', '')

    def headword(self):
        return self.store.get('headword', '')

    def year(self):
        return self.store.get('year', '2000')

    def entrytype_options(self):
        if self.store.get('entrytype'):
            default = False
        else:
            default = True
        options = []
        for option in entrytypes:
            if (option[0] == self.store.get('entrytype') or
                    (default and option[0] == 'any')):
                options.append((option[0], option[1], True))
            else:
                options.append((option[0], option[1], False))
        return options

    def wordclass_options(self):
        if self.store.get('wordclass'):
            default = False
        else:
            default = True
        options = []
        for option in wordclasses:
            if (option[0] == self.store.get('wordclass') or
                (default and option[0] == 'any')):
                options.append((option[0], option[1], True))
            else:
                options.append((option[0], option[1], False))
        return options

    def sort_options(self):
        if self.store.get('sortBy'):
            default = False
        else:
            default = True
        options = []
        for option in sorts:
            if (option[0] == self.store.get('sortBy') or
                (default and option[0] == 'd')):
                options.append((option[0], option[1], True))
            else:
                options.append((option[0], option[1], False))
        return options

    def frequency_min_options(self):
        if self.store.get('frequencyBandMin'):
            default = False
        else:
            default = True
        options = []
        for option in bands:
            if (option[0] == int(self.store.get('frequencyBandMin', 10)) or
                (default and option[0] == 1)):
                options.append((option[0], option[1], True))
            else:
                options.append((option[0], option[1], False))
        return options

    def frequency_max_options(self):
        if self.store.get('frequencyBandMax'):
            default = False
        else:
            default = True
        options = []
        for option in bands:
            if (option[0] == int(self.store.get('frequencyBandMax', 10)) or
                (default and option[0] == 8)):
                options.append((option[0], option[1], True))
            else:
                options.append((option[0], option[1], False))
        return options

    def include_date_ghosts(self):
        if self.store.get('includeDateGhosts', False):
            return True
        else:
            return False

    def include_freq_ghosts(self):
        if self.store.get('includeFreqGhosts', False):
            return True
        else:
            return False
