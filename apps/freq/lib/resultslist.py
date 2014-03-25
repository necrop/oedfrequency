import re

from ..models import Lemma
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .searchform import sorts as sort_options

results_per_page = 50


class ResultsList(object):

    def __init__(self, request):
        self.path = request.path
        self.args = request.GET

    def list_results(self):
        lemma = self.args.get('lemma', '')
        headword = self.args.get('headword', None)
        wordclass = self.args.get('wordclass')
        entrytype = self.args.get('entrytype')
        fb_min = int(self.args.get('fbMin'))
        fb_max = int(self.args.get('fbMax'))
        year = int(self.args.get('year', 2012))
        sortmode = self.args.get('sort', 'd')
        ghosts = {'date': self.args.get('dghosts', False),
                  'frequency': self.args.get('fghosts', False), }
        page_num = int(self.args.get('page', 1))

        lemma = lemma.lower()
        lemma = re.sub('[^a-z*_,]', '', lemma)
        lemma_group = []
        if len(lemma.split(',')) > 1:
            lemma_group = [l.replace('_', '').replace('*', '') for l in
                           lemma.split(',')]
            lemma_group = [l for l in lemma_group if l]
        elif len(lemma.split('_', 1)) == 2:
            lemma_from, lemma_to = lemma.split('_', 1)
        elif lemma.endswith('*'):
            lemma_from = lemma.replace('*', '')
            lemma_to = lemma.replace('*', '') + 'zz'
        else:
            lemma_from = lemma_to = lemma

        for type in ('date', 'frequency'):
            if not ghosts[type] or ghosts[type] == 'False':
                ghosts[type] = False
            else:
                ghosts[type] = True

        # Determine which frequency columns to use from the database model
        bandfield, freqfield = columns_from_year(year)

        # first cut of qset (based on alphabetical lemma range)
        if lemma_group:
            qset = Lemma.objects.filter(alphasort__in=lemma_group)
        else:
            qset = Lemma.objects.filter(alphasort__gte=lemma_from,
                                        alphasort__lte=lemma_to,)
        if not wordclass in ('any', 'all'):
            qset = qset.filter(wordclass=wordclass.upper())

        if headword:
            qset = qset.filter(entry__alphasort=headword)

        if entrytype == 'main':
            qset = qset.filter(mainentry=True)
        elif entrytype == 'subentries':
            qset = qset.filter(mainentry=False)

        # Alias the appropriate frequency band and raw frequency columns
        #  as 'band' and 'frequency'
        qset = qset.extra(select={'band': bandfield, 'frequency': freqfield})

        # Identify or filter out frequency ghosts
        if not ghosts['frequency']:
            kwargs = {bandfield + '__gte': fb_min, bandfield + '__lte': fb_max}
            qset = qset.filter(**kwargs)
        else:
            qset = qset.extra(select={'is_freq_ghost': '%s < %d or %s > %d' %
                                      (bandfield, fb_min, bandfield, fb_max,)})

        # Identify or filter out date ghosts
        if not ghosts['date']:
            qset = qset.filter(startdate__lte=year, enddate__gte=year)
        else:
            qset = qset.extra(select={'is_date_ghost': 'startdate > %d or enddate < %d' %
                                      (year, year,)})

        # Sort results
        if sortmode == 'l':
            pass
        elif sortmode == 'freqd':
            qset = qset.order_by('-' + freqfield, bandfield)
        elif sortmode == 'freqa':
            qset = qset.order_by(freqfield, '-' + bandfield)
        elif sortmode == 'fda':
            qset = qset.order_by('startdate')
        elif sortmode == 'fdd':
            qset = qset.order_by('-startdate')
        elif sortmode == 'increase':
            qset = [e for e in qset if e.delta() is not None]
            qset = sorted(qset, key=lambda e: e.delta(), reverse=True)
        elif sortmode == 'decrease':
            qset = [e for e in qset if e.delta() is not None]
            qset = sorted(qset, key=lambda e: e.delta())

        # slice into a single page of results
        paged = Paginator(qset, results_per_page)
        try:
            results = paged.page(page_num)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            results = paged.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            results = paged.page(paged.num_pages)

        return results, self.paginators(results)

    def paginators(self, results):
        """
        Generate previous/next links
        """
        prevlink = None
        nextlink = None
        if results.has_other_pages():
            current_page = self.path
            args = {k: v for k, v in self.args.items()}
            if results.has_previous():
                args['page'] = str(results.previous_page_number())
                prevlink = current_page + '?' + '&'.join('%s=%s' % (k, v,)
                           for k, v in args.items())
            if results.has_next():
                args['page'] = str(results.next_page_number())
                nextlink = current_page + '?' + '&'.join('%s=%s' % (k, v,)
                           for k, v in args.items())
        return prevlink, nextlink

    def sorters(self):
        """
        Links used to re-sort the current results set
        """
        sortlinks = []
        current_page = self.path
        for value, readable in sort_options:
            args = {k: v for k, v in self.args.items()}
            args['sort'] = value
            link = current_page + '?' + '&'.join('%s=%s' % (k, v,)
                                                 for k, v in args.items())
            sortlinks.append((link, readable))
        return sortlinks


def columns_from_year(year):
    if year < 1800:
        y = 1750
    elif year < 1850:
        y = 1800
    elif year < 1900:
        y = 1850
    elif year < 1950:
        y = 1900
    elif year < 2000:
        y = 1950
    else:
        y = 2000
    return 'fb%d' % y, 'f%d' % y
