import re


def url_constructor(args, page_num):
    args = {k: v for k, v in args.items() if v.strip()}

    lemma = sanitize(args.get('lemma', 'a_zzz'))
    headword = sanitize(args.get('headword', ''), alpha_only=True)
    year = int(args.get('year', 2000))
    entrytype = args.get('entrytype', 'any')
    fb_min = int(args.get('frequencyBandMin', 1))
    fb_max = int(args.get('frequencyBandMax', 8))
    sort = args.get('sortBy', 'd')
    wordclass = args.get('wordclass', 'any')
    date_ghosts = args.get('includeDateGhosts', False)
    freq_ghosts = args.get('includeFreqGhosts', False)

    qstring = ('?lemma=%s&wordclass=%s&year=%d&fbMin=%d&fbMax=%d&entrytype=%s'
               % (lemma, wordclass, year, fb_min, fb_max, entrytype))
    if headword:
        qstring += '&headword=%s' % headword
    if sort != 'd':
        qstring += '&sort=%s' % sort
    if date_ghosts:
        qstring += '&dghosts=True'
    if freq_ghosts:
        qstring += '&fghosts=True'
    if page_num is not None and page_num > 1:
        qstring += '&page=%d' % page_num

    return qstring


def ngram_url(content):
    return ('http://books.google.com/ngrams/graph?' +
           'content=%s' % content +
           '&year_start=1750&year_end=2008&corpus=15&smoothing=3')


def sanitize(lemma, alpha_only=False):
    l = re.sub(r'[^a-z*_,]', '', lemma.lower())
    l = re.sub(r'^[_,]*|[_,]*$', '', l)
    if alpha_only:
        l = re.sub(r'[^a-z]', '', l)
    return l
