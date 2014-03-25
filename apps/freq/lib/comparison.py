import json

from ..models import Lemma
from .urlconstructor import ngram_url
from .stripzeroes import strip_zeroes


class Comparison(object):

    def __init__(self, idlist):
        self.idlist = idlist

    def entries(self):
        try:
            return self._entries
        except AttributeError:
            ids = []
            for id in self.idlist.split('+'):
                if not id in ids:
                    ids.append(id)

            self._entries = [Lemma.objects.get(id=id) for id in ids]

            # Add e.remove attribute, which is a list of all IDs *except* for
            #  this entry - this provides the hook for removing the current
            #  entry from comparison
            for e in self._entries:
                if len(self._entries) > 1:
                    e.remove = '+'.join([id for id in ids if id != str(e.id)])
                else:
                    e.remove = None

            return self._entries

    def top2_entries(self):
        try:
            return self._top2_entries
        except AttributeError:
            tops = self.entries()[:]
            tops.sort(key=lambda e: e.fmodern, reverse=True)
            self._top2_entries = tops[0:2]
            return self._top2_entries

    def label_list(self):
        return ', '.join(["'%s'" % (e.label,) for e in self.entries()])

    def label_list_tagged(self):
        return ', '.join(["'%s'" % (e.label_tagged(),) for e in self.entries()])

    def ngram_query(self):
        return ngram_url(','.join(set([e.lemma() for e in self.entries()])))

    def add_to_recentlycompared(self, recent):
        if not self.idlist in [r[0] for r in recent]:
            recent.append((self.idlist, self.label_list_tagged()))
            if len(recent) > 10:
                recent.pop(0)

    def tojson(self):
        struct = []
        for e in [e for e in self.entries() if e.table()]:
            struct.append({'label': e.label,
                           'series': strip_zeroes(e.table().moving_average())})
        return json.dumps(struct)

    def ratio_json(self):
        """
        Ratios of highest-rated entry's frequencies to
        second-highest_rated entry's corresponding frequencies
        """
        ratios = []
        tops = self.top2_entries()
        if len(tops) == 2:
            t2_hash = {period: value for period, value in
                       tops[1].table().interpolated() if value > 0}
            for period, value in tops[0].table().interpolated():
                if value > 0 and period in t2_hash:
                    ratio = value / t2_hash[period]
                    ratio = float('%.2g' % ratio)
                    ratios.append((period, ratio))
        return json.dumps(ratios)

    def filter_adders(self, recently_viewed):
        current_ids = set([e.id for e in self.entries()])
        return [e for e in recently_viewed if not e[0] in current_ids]

    def grand_table(self):
        try:
            return self._grand_table
        except AttributeError:
            tables = [t.table().interpolated() for t in self.entries()
                      if t.table()]
            periods = [p[0] for p in tables[0]]
            values = []
            for i in range(0, len(periods)):
                row = [t[i][1] for t in tables]
                values.append(row)
            self._grand_table = zip(periods, values)
            return self._grand_table

