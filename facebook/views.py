from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView
from django.core.mail import send_mail
from pyfb import Pyfb
from pyfb.auth import ALL_PERMISSIONS
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.contrib.auth.models import User
# Create your views here.
import simplejson as json
import requests
from facebook.models import FacebookUser, BlackListedWords
from facebook.forms import BlackListWordsForm
from django.core.urlresolvers import reverse


AUTHORIZE_URL = 'https://graph.facebook.com/oauth/authorize?'
ACCESS_TOKEN_URL = 'https://graph.facebook.com/v2.3/oauth/access_token?'
CLIENT_ID = '177316008955964'
CLIENT_APP_SECRET = 'a98cec4142c3cd8ed35800b48696f136'
GRANT_TYPE = 'client_credentials'
REDIRECT_URL = 'http://dev.ahfctoolkit.com.ngrok.com/facebook_login_success'
SENDER_EMAIL = 'milind.sakya@gmail.com'
RECIPIENT_EMAIL = 'upechhya97@gmail.com'
# This is a short lived token for now. Need to get long lasting token
ACCESS_TOKEN = 'CAACEdEose0cBAB5ZAJo5A9GlVxvDUdY0Nrfz65jofmGPLZBVZAKigqxjsdT5oZCzCTGstPAY38cHvrJx8y6sHneNC6TOXgaQudB72HuZBy657QE9qstGAay6AZB1miPgZAZC6mCyUhA4xvPw6rLw5NYy6UnmkBUtYYuzB6jeFujycePoUfxsSl7tZAWipdfFMFfenZAOtp4FN3VzsAjhk9lL1L'
#ACCESS_TOKEN = 'CAACEdEose0cBAHtUnw8bNI0RUWA6ML8JBroSKt7VPlhcp6f7pBQjxCKXalcwzngkGibHsT7aPReRMg4e0iq4sM3Fq0g9lO4AabqsBjvKvpaWn98x3MNbGTCxvfZCP7OiUlp7BRjJ202SN1vbXkMs9db3TUkVHM4LV4mQ0OuRUt6wFeAQUgh3h0hiTNUu2hB8101OoZB8chayEeTLZAp'


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
    auth_code_url = facebook.get_auth_code_url(redirect_uri=REDIRECT_URL)
    return HttpResponseRedirect(auth_code_url)


def facebook_login_success(request):
    code = request.GET.get('code')
    facebook = Pyfb(CLIENT_ID)
    access_token = facebook.get_access_token(CLIENT_APP_SECRET, code, redirect_uri=REDIRECT_URL)
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
            last_name=me.last_name
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
        access_token = FacebookUser.objects.get(user=user).access_token
        # Get the feed
        feeds = self.get_feed(access_token=access_token)
        self.get_comments_having_blacklisted_words(feeds, user)
        print feeds
        #self.delete_them()
        return HttpResponse(json.dumps(self.blacklist_comments))

    def delete_them(self):
        for comment in self.blacklist_comments:
            response = requests.delete(self.signed_url(self.delete_url.format(comment['id'])))
            send_mail(
                'Facebook blacklist comment deleted',
                'This message was deleted:\n {}'.format(comment['message']),
                SENDER_EMAIL,
                [RECIPIENT_EMAIL],
            )
            print response.content

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
    if request.method == 'GET':
        request_context = RequestContext(request)
        request_context.push({
            'form': form,
            'user': request.user
        })
        return render_to_response('blacklist_words.html', request_context)
    else:
        form = BlackListWordsForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
        else:
            return HttpResponse(form.errors)

