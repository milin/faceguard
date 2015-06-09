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
from django.template import RequestContext
from django.views.generic import TemplateView
from facebook.forms import BlackListWordsForm
from facebook.models import BlackListedWords, FacebookUser
from pyfb import Pyfb
from django.conf import settings


def facebook_login(request):
    facebook = Pyfb(CLIENT_ID, permissions=[
        'publish_actions',
        'publish_pages',
        'user_photos',
        'user_posts',
        'manage_pages',
        'user_about_me',
        'email'
    ])
    auth_code_url = facebook.get_auth_code_url(redirect_uri=settings.REDIRECT_URL)
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
    blacklist_words = [
        'nambara',
        'lol',
        'patta',
        'pathetic',
        'explanation',
        'Cherly',
        'khemanbhai',
        'enticing',
        'Lovely',
        'Yup',
        'capturing'
    ]

    def __init__(self):
        self.blacklist_comments = []
        super(Facebook, self).__init__()

    def signed_url(self, url, access_token):
        return '{}?access_token={}'.format(url, access_token)

    def get_feed(self, access_token=None):
        if not access_token:
            access_token = ACCESS_TOKEN
        data = {
            'access_token': access_token
        }
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
        for comment in self.blacklist_comments:
            #response = requests.delete(self.signed_url(self.delete_url.format(comment['id'])))
            send_mail(
                'Facebook blacklist comment deleted',
                'This message was deleted:\n {}'.format(comment['message']),
                settings.SENDER_EMAIL,
                [request.user.email],
            )
            #print response.content

def login_user(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
    request_context = RequestContext(request)
    request_context.push({
        'state': state,
        'username': username
    })
    return render_to_response('auth.html', request_context)


def blacklist_words(request):
    form = BlackListWordsForm(request.user)
    fb_user = FacebookUser.objects.get(user=request.user)

    if request.method == 'GET':
        initial = BlackListedWords.objects.filter(user=fb_user)
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
