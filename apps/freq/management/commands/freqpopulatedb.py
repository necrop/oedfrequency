"""
Management wrapper for running database build processes
"""

from django.core.management.base import BaseCommand

from stringtools import lexical_sort
from lex.oed.resources.frequencyiterator import FrequencyIterator
from lex.oed.resources.entryrank import EntryRank
from lex.oed.resources.vitalstatistics import VitalStatisticsCache

from apps.freq.models import Entry, Lemma

NULL_FREQUENCY_BAND = 8
FREQUENCY_FIELDS = (1750, 1800, 1850, 1880, 1900, 1920, 1940, 1950, 1960,
                    1970, 1980, 1990, 2000)
BAND_FIELDS = (1750, 1800, 1850, 1900, 1950, 2000)

INPUT_DIR = '/home/james/j/work/lex/oed/projects/frequency/full_frequency_data'
LABEL_LENGTH = Lemma._meta.get_field('label').max_length
ALPHASORT_LENGTH = Lemma._meta.get_field('alphasort').max_length
DEFINITION_LENGTH = Lemma._meta.get_field('definition').max_length


class Command(BaseCommand):
    help = 'Run database build processes for OED Frequency'

    def handle(self, *args, **options):
        #Empty the tables
        Lemma.objects.all().delete()
        #Entry.objects.all().delete()
        #populate_entries()
        populate_lemmas()


def populate_entries():
    vsc = VitalStatisticsCache()
    entries = []
    for entry in vsc.entries:
        row = Entry(id=entry.id,
                    label=entry.label[:LABEL_LENGTH],
                    alphasort=lexical_sort(entry.headword)[:ALPHASORT_LENGTH])
        entries.append(row)

        if len(entries) > 1000:
            Entry.objects.bulk_create(entries)
            entries = []

    Entry.objects.bulk_create(entries)


def populate_lemmas():

    ranking = EntryRank()
    iterator = FrequencyIterator(in_dir=INPUT_DIR, message='Populating database')
    count = 0
    entries = []
    for e in iterator.iterate():
        count += 1
        if e.is_obsolete():
            last_date = e.end
        else:
            last_date = 2050

        if e.is_main_entry:
            try:
                rank = ranking.entry(e.id).rank
            except AttributeError:
                rank = 250000
        else:
            rank = None

        if e.is_main_entry:
            xrnode = None
        else:
            xrnode = e.xrnode

        entry = Lemma(
            xrnode=xrnode,
            label=e.label[:LABEL_LENGTH],
            alphasort=e.alphasort()[:ALPHASORT_LENGTH],
            definition=e.definition[:DEFINITION_LENGTH],
            dictsort=count,
            json=e.todict(),
            wordclass=e.wordclass() or 'X',
            startdate=e.start,
            enddate=last_date,
            rank=rank,
            entry_id=e.id,
            mainentry=e.is_main_entry,
        )

        # Frequency + frequency-band fields
        if not e.has_frequency_table():
            for year in FREQUENCY_FIELDS:
                field = 'f%d' % year
                entry.__dict__[field] = 0
            entry.fmodern = 0
            for year in BAND_FIELDS:
                field = 'fb%d' % year
                entry.__dict__[field] = NULL_FREQUENCY_BAND
            entry.fbmodern = NULL_FREQUENCY_BAND
        else:
            for year in FREQUENCY_FIELDS:
                field = 'f%d' % year
                entry.__dict__[field] = e.frequency_table().frequency(year=year)
            entry.fmodern = e.frequency_table().frequency(period='modern')
            for year in BAND_FIELDS:
                field = 'fb%d' % year
                entry.__dict__[field] = e.frequency_table().band(year=year)
            entry.fbmodern = e.frequency_table().band(period='modern')

        entries.append(entry)
        if len(entries) > 1000:
            Lemma.objects.bulk_create(entries)
            entries = []

    Lemma.objects.bulk_create(entries)
