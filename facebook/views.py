import requests
import simplejson as json
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import (
    HttpResponse,
    HttpResponseRedirect,
    render_to_response,
)
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.generic import TemplateView
from facebook.forms import BlackListWordsForm
from facebook.models import (
    BlackListedWords,
    FacebookUser,
    DeletedComments
)
from pyfb import Pyfb
from django.conf import settings


def facebook_login(request):
    # Gets the auth redirect url with code provided from facebook.
    facebook = Pyfb(
        settings.CLIENT_ID,
        permissions=settings.FACEBOOK_SCOPE
    )
    auth_code_url = facebook.get_auth_code_url(
        redirect_uri=settings.REDIRECT_URL
    )
    return HttpResponseRedirect(auth_code_url)


def facebook_login_success(request):
    code = request.GET.get('code')
    facebook = Pyfb(settings.CLIENT_ID)
    access_token = facebook.get_access_token(
        settings.CLIENT_APP_SECRET,
        code,
        redirect_uri=settings.REDIRECT_URL
    )
    me = facebook.get_myself()

    try:
        fb_user = FacebookUser.objects.get(email_address=me.email)
        fb_user.access_token = access_token
        fb_user.save()
        user = fb_user.user
    except FacebookUser.DoesNotExist:
        user = User.objects.create(
            username=me.email,
            first_name=me.first_name,
            last_name=me.last_name,
            email=me.email
        )
        user.set_password(me.email)
        user.save()
        fb_user = FacebookUser.objects.create(
            first_name = me.first_name,
            last_name = me.last_name,
            access_token = access_token,
            email_address = me.email,
            username=me.email,
            user=user
        )

    user = authenticate(
        username=me.email,
        password=me.email
    )
    # log the user in
    login(request, user)
    return HttpResponseRedirect(reverse('blacklist_words'))


class Facebook(TemplateView):
    feed_url = 'https://graph.facebook.com/me/feed'
    delete_url = 'https://graph.facebook.com/v2.3/{}'
    feed = None

    def __init__(self):
        self.blacklist_comments = []
        super(Facebook, self).__init__()

    def signed_url(self, url, access_token):
        return '{}?access_token={}'.format(url, access_token)

    def get_feed(self, access_token=None):
        response = requests.get(self.signed_url(self.feed_url, access_token))
        self.feed = json.loads(response.content)['data']
        return self.feed

    def get_comments_having_blacklisted_words(self, feeds, user):
        for feed in feeds:
            self.get_blacklisted_comments_from_post(feed, user)

    def get_blacklisted_comments_from_post(self, feed, user):
        fb_user = FacebookUser.objects.get(user=user)
        blacklist_words = [bl.word for bl in BlackListedWords.objects.filter(user=fb_user)]
        try:
            for comment in feed['comments']['data']:
                if set(comment['message'].split(' ')).intersection(set(blacklist_words)):
                    self.blacklist_comments.append(comment)
        except Exception as e:
            print e

    def get(self, request):
        user = request.user
        fb_user = FacebookUser.objects.get(user=user)
        access_token = fb_user.access_token
        # Get the feed
        feeds = self.get_feed(access_token=access_token)
        self.get_comments_having_blacklisted_words(feeds, user)
        print feeds
        self.delete_them(request)
        return HttpResponse(json.dumps(self.blacklist_comments))

    def delete_them(self, request):
        user = request.user
        fb_user = FacebookUser.objects.get(user=user)
        access_token = fb_user.access_token
        for comment in self.blacklist_comments:
            response = requests.delete(self.signed_url(
                self.delete_url.format(comment['id']),
                access_token
            ))
            self.store_comment_to_be_deleted(fb_user, comment)
            send_mail(
                'Facebook blacklist comment deleted',
                'This message was deleted:\n {}'.format(comment['message']),
                settings.SENDER_EMAIL,
                [request.user.email],
            )

    def store_comment_to_be_deleted(fb_user, comment):
        """
        Store the comment to be deleted and it's metadata for reviewing
        purposes.
        """
        DeletedComments.objects.create(
            message = comment['message'],
            message_by = comment['from']['name'],
            message_id = comment['id'],
            user=fb_user,
        )


@login_required
def blacklist_words(request):
    form = BlackListWordsForm(request.user)
    fb_user = FacebookUser.objects.get(user=request.user)

    if request.method == 'GET':
        initial = BlackListedWords.objects.filter(user=fb_user)
        initial_words = []
        if initial:
            initial_words = [i.word for i in initial]
        request_context = RequestContext(request)
        request_context.push({
            'form': form,
            'user': request.user,
            'initial_words': initial_words
        })
        return render_to_response('blacklist_words.html', request_context)
    else:
        form = BlackListWordsForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('blacklist_words'))
        else:
            return HttpResponse(form.errors)

def homepage(request):
    return render_to_response('homepage.html')

