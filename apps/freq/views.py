from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


@login_required
def homepage(request):
    params = {'page_title': 'OED Frequency',}
    return render(request, 'freq/home.html',
                  _add_base_params(params, request))


def infopage(request, **kwargs):
    pagename = kwargs.get('pagename')
    title = pagename.replace('_', ' ')
    params = {'page_title': title.title(),}
    template = 'freq/infopages/%s.html' % pagename,
    return render(request, template, _add_base_params(params, request))


def search_form(request):
    from .lib.searchform import SearchForm
    if 'oedfrequency' in request.session:
        form = SearchForm(request.session['oedfrequency'])
    else:
        form = SearchForm({})
    params = {'page_title': 'Search', 'form': form,}
    return render(request, 'freq/search.html',
                  _add_base_params(params, request))


def quicksearch(request):
    from .lib.urlconstructor import url_constructor
    if request.method == 'POST':
        request.session['oedfrequency_quicksearch'] = request.POST.get('lemma', '').strip()

        querystring = url_constructor(request.POST, None)
        url = reverse('freq:results') + querystring
        return HttpResponseRedirect(url)
    else:
        return redirect(homepage)


def search(request):
    from .lib.urlconstructor import url_constructor
    if request.method == 'POST':
        if not 'oedfrequency' in request.session:
            request.session['oedfrequency'] = {}
        newlist = {k: v for k, v in request.session['oedfrequency'].items()
                   if not k.startswith('csrf')}
        for key, value in request.POST.items():
            newlist[key] = value
        for j in ('includeDateGhosts', 'includeFreqGhosts'):
            if j in request.POST.items():
                newlist[j] = True
            else:
                newlist[j] = False
        request.session['oedfrequency'] = newlist
        querystring = url_constructor(request.POST, None)
        url = reverse('freq:results') + querystring
        return HttpResponseRedirect(url)
    else:
        return redirect(homepage)


@login_required
def results(request, **kwargs):
    from .lib.resultslist import ResultsList
    results_manager = ResultsList(request)
    res, pagination = results_manager.list_results()
    sorters = results_manager.sorters()
    num_results = res.paginator.count

    if num_results == 0:
        title = 'No results found'
    elif num_results == 1:
        title = '1 result'
    else:
        title = '%d - %d of %d results' % (res.start_index(), res.end_index(),
                                           num_results,)

    if 1 < num_results <= 10:
        comparators = '+'.join([str(r.id) for r in res])
    else:
        comparators = None

    # Render
    params = {'page_title': title,
              'results': res, 'pagination': pagination, 'sorters': sorters,
              'comparators': comparators,}
    return render(request, 'freq/results.html',
                  _add_base_params(params, request))


@login_required
def entry_display(request, **kwargs):
    from .models import Lemma
    try:
        lemma = Lemma.objects.get(id=kwargs.get('id'))
    except Lemma.DoesNotExist:
        raise Http404
    else:
        # Add this entry to recently_viewed
        if not 'oedfrequency_recentlyviewed' in request.session:
            request.session['oedfrequency_recentlyviewed'] = []
        lemma.add_to_recentlyviewed(request.session['oedfrequency_recentlyviewed'])
        request.session.modified = True

        params = {'page_title': lemma.label_tagged(), 'lemma': lemma}
        return render(request, 'freq/entry.html',
                      _add_base_params(params, request))


@login_required
def compare(request, **kwargs):
    from .lib.comparison import Comparison
    cp = Comparison(kwargs.get('idlist'))

    # Add this comparison to recently_compared
    if not 'oedfrequency_recentlycompared' in request.session:
        request.session['oedfrequency_recentlycompared'] = []
    cp.add_to_recentlycompared(request.session['oedfrequency_recentlycompared'])
    request.session.modified = True

    adders = cp.filter_adders(request.session.get('oedfrequency_recentlyviewed', []))
    params = {'page_title': 'Compare frequencies',
              'comparison': cp,
              'adders': adders,}
    return render(request, 'freq/comparison.html',
                  _add_base_params(params, request))


def _add_base_params(params, request):
    params['recent_entries'] = request.session.get('oedfrequency_recentlyviewed', [])
    params['recent_comp'] = request.session.get('oedfrequency_recentlycompared', [])
    params['qsearchvalue'] = request.session.get('oedfrequency_quicksearch', '')
    params['url_path'] = request.path
    return params
