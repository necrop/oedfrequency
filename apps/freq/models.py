import re
import json

from django.db import models
from jsonfield import JSONField

from .lib.urlconstructor import ngram_url
from .lib.frequencytable import FrequencyTable
from .lib.readablepos import readable_pos
from .lib.stripzeroes import strip_zeroes

LABEL_TAGGER = re.compile(r'^(.*?), (.*)$')
OED_ONLINE_STUB = 'http://www.oed.com/view/Entry/'
DICT_BROWSER_STUB = 'https://poed.uk.hub.oup.com/dicbrowser/displayentry.jsp?'


class Entry(models.Model):
    label = models.CharField(max_length=50)
    alphasort = models.CharField(max_length=30, db_index=True)

    def dictbrowser_link(self):
        return '%sidEntry=%s' % (DICT_BROWSER_STUB, self.id)

    def oed_online_link(self):
        return '%s%s' % (OED_ONLINE_STUB, self.id)

    def xrid(self):
        return self.id

    def label_tagged(self):
        return _tag_label(self.label)


class Lemma(models.Model):
    entry = models.ForeignKey(Entry)
    xrnode = models.IntegerField(null=True)
    json = JSONField(null=True)
    alphasort = models.CharField(max_length=30, db_index=True)
    dictsort = models.IntegerField(db_index=True)
    label = models.CharField(max_length=50)
    mainentry = models.BooleanField(db_index=True)
    definition = models.CharField(max_length=60, blank=True)
    wordclass = models.CharField(max_length=6, db_index=True)
    startdate = models.SmallIntegerField()
    enddate = models.SmallIntegerField()
    rank = models.IntegerField(null=True)
    f1750 = models.FloatField()
    f1800 = models.FloatField()
    f1850 = models.FloatField()
    f1880 = models.FloatField()
    f1900 = models.FloatField()
    f1920 = models.FloatField()
    f1940 = models.FloatField()
    f1950 = models.FloatField()
    f1960 = models.FloatField()
    f1970 = models.FloatField()
    f1980 = models.FloatField()
    f1990 = models.FloatField()
    f2000 = models.FloatField()
    fmodern = models.FloatField()
    fb1750 = models.SmallIntegerField(db_index=True)
    fb1800 = models.SmallIntegerField(db_index=True)
    fb1850 = models.SmallIntegerField(db_index=True)
    fb1900 = models.SmallIntegerField(db_index=True)
    fb1950 = models.SmallIntegerField(db_index=True)
    fb2000 = models.SmallIntegerField(db_index=True)
    fbmodern = models.SmallIntegerField(db_index=True)

    def __str__(self):
        return '%s (%d)' % (self.label, self.xrid)

    class Meta:
        ordering = ['alphasort', 'dictsort']

    def lemma(self):
        l = re.sub(r', .*$', '', self.label)
        l = re.sub(r' \| .*$', '', l)
        return l

    def label_tagged(self):
        return _tag_label(self.label)

    def xrid(self):
        return self.entry.id

    def ngram_link(self):
        return ngram_url(self.lemma())

    def dictbrowser_link(self):
        if self.xrnode:
            return '%sidEntry=%s&isEnID=%s' % (DICT_BROWSER_STUB, self.xrid(), self.xrnode)
        else:
            return '%sidEntry=%s' % (DICT_BROWSER_STUB, self.xrid())

    def oed_online_link(self):
        if self.xrnode:
            return '%s%s#eid%s' % (OED_ONLINE_STUB, self.xrid(), self.xrnode)
        else:
            return '%s%s' % (OED_ONLINE_STUB, self.xrid())

    def date_range(self):
        if self.enddate > 2000:
            return '%d\u2015' % self.startdate
        else:
            return '%d\u2014%d' % (self.startdate, self.enddate,)

    def table(self):
        try:
            return self._table
        except AttributeError:
            if self.json and self.json['ft']:
                self._table = FrequencyTable(data=self.json['ft'])
            else:
                self._table = None
            return self._table

    def grand_table(self):
        try:
            return self._grand_table
        except AttributeError:
            if not self.table():
                self._grand_table = []
            else:
                tables = [t['table'].interpolated() for t in self.types()]
                tables.append(self.table().interpolated())
                periods = [p[0] for p in tables[0]]
                values = []
                for i in range(0, len(periods)):
                    row = [t[i][1] for t in tables]
                    values.append(row)
                self._grand_table = zip(periods, values)
            return self._grand_table

    def types(self):
        try:
            return self._types
        except AttributeError:
            self._types = []
            if self.json:
                for block in self.json['wordclasses']:
                    for type_unit in block['types']:
                        if type_unit['ft']:
                            type_unit['table'] = FrequencyTable(data=type_unit['ft'])
                            type_unit['label'] = '%s (%s)' % (
                                type_unit['form'],
                                readable_pos(type_unit['pos'], verbose=True),
                            )
                            self._types.append(type_unit)
            self._types.sort(key=lambda t: t['table'].frequency(), reverse=True)
            return self._types

    def types_labels(self):
        return [t['label'] for t in self.types()]

    def types_string(self):
        return ', '.join(self.types_labels())

    def main_series(self):
        if self.table():
            series_raw = strip_zeroes(self.table().interpolated())
            series_smooth = strip_zeroes(self.table().moving_average())
            series = _align_series(series_smooth, series_raw)
        else:
            series = []
        return json.dumps(series)

    def types_series(self):
        series = []
        for t in self.types():
            series_raw = strip_zeroes(t['table'].interpolated())
            series_smooth = strip_zeroes(t['table'].moving_average())
            tseries = _align_series(series_smooth, series_raw)
            series.append({'label': t['label'], 'series': tseries,})
        return json.dumps(series)

    def delta(self):
        if self.fb1800 <= 7 and self.fbmodern <= 7:
            return self.fmodern / self.f1800
        else:
            return None

    def add_to_recentlyviewed(self, recent):
        if not self.id in [r[0] for r in recent]:
            recent.append((self.id, self.label_tagged()))
            if len(recent) > 10:
                recent.pop(0)


def _align_series(raw, smoothed):
    smoothed_hash = {period: f for period, f in smoothed}
    series = []
    for period, raw_frequency in raw:
        try:
            smoothed_frequency = smoothed_hash[period]
        except KeyError:
            smoothed_frequency = 0
        series.append((period, raw_frequency, smoothed_frequency))
    return series


def _tag_label(label):
    m = LABEL_TAGGER.search(label)
    if m is not None:
        lt = '%s, <i>%s</i>' % (m.group(1), m.group(2),)
        return re.sub(r'/(\d+)', r'<sup>\1</sup>', lt)
    else:
        return label