from django.contrib.auth.models import User
from django.db import models


class FacebookUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    access_token = models.TextField()
    email_address = models.EmailField(max_length=50)
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    user=models.ForeignKey(User)
    blacklist_words = models.TextField()


    def __str__(self):
        return self.first_name

class BlackListedWords(models.Model):
    word = models.CharField(max_length=100)
    user = models.ForeignKey(FacebookUser)

    def __str__(self):
        return self.word

