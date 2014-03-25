from django.conf.urls import patterns, url

urlpatterns = patterns('apps.freq.views',
    url(r'^/?$', 'homepage', name='homepage'),
    url(r'^home$', 'homepage', name='homepage'),
    url(r'^about/(?P<pagename>[A-Za-z0-9_-]+)$', 'infopage', name='infopage'),
    url(r'^searchform$', 'search_form', name='searchform'),
    url(r'^search$', 'search', name='search'),
    url(r'^quicksearch$', 'quicksearch', name='quicksearch'),
    url(r'^results$', 'results', name='results'),
    url(r'^entry/(?P<id>\d+)$', 'entry_display', name='entry'),
    url(r'^compare/(?P<idlist>[0-9\+]+)$', 'compare', name='compare'),
)
