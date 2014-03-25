from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib import admin

from apps.root.views import homepage

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'htclassifier.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', homepage),
    url(r'^home/?$', homepage),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, name='logout'),
    url(r'^r/', include('apps.freq.urls', namespace='freq', app_name='freq')),
)
