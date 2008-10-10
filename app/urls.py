from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^$', 'proof.views.index'),

    (r'^proofs/start$', 'proof.views.proof_start'),
    (r'^proofs/(\d+)/$', 'proof.views.proof_detail'),
    (r'^proofs/(\d+)/advance$', 'proof.views.proof_advance'),

    (r'^parser/$', 'proof.views.parser'),
    (r'^definitions/$', 'proof.views.definitions'),
    (r'^rules/$', 'proof.views.rules'),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': '/home/cap/thesis/cheqed/app/media'}),

    (r'^admin/(.*)', admin.site.root),
)
