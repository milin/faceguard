from django.conf.urls import patterns, include, url

from django.contrib import admin
from facebook.views import (
    Facebook,
    facebook_login_success,
    facebook_login,
    blacklist_words,
    homepage
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
    url(r'^blacklist', blacklist_words, name='blacklist_words'),
    url(r'^home', homepage, name='home'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',{'next_page': '/accounts/login'})
)
