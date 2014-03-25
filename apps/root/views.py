from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def homepage(request):
    """
    Home page
    """
    new_url = reverse('freq:homepage', kwargs={})
    return HttpResponseRedirect(new_url)
    #params = {}
    #return render(request, 'root/home.html', params)
