from django.conf.urls import patterns, include, url

from django.contrib import admin
from facebook.views import (
    Facebook,
    facebook_login_success,
    facebook_login,
    login_user,
    blacklist_words
)
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'faceguard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^delete_comment/', Facebook.as_view()),
    #url(r'^callback/', get_accesstoken),
    url(r'^facebook_login_success', facebook_login_success),
    url(r'^facebook_login', facebook_login, name='facebook_login'),
    url(r'^login', login_user),
    url(r'^blacklist', blacklist_words, name='blacklist_words')
)
