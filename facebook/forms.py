from django import forms
from facebook.models import (
    FacebookUser,
    BlackListedWords
)

class BlackListWordsForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(BlackListWordsForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FacebookUser
        fields = ['blacklist_words']

    def save(self):
        fb_user = FacebookUser.objects.get(user=self.user)
        data = self.cleaned_data
        blacklist_words = data['blacklist_words'].split(' ')
        for word in blacklist_words:
            BlackListedWords.objects.create(word=word, user=fb_user)
