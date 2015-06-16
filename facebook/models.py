from django.contrib.auth.models import User
from django.db import models


class FacebookUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    access_token = models.TextField()
    email_address = models.EmailField(max_length=50)
    username=models.CharField(max_length=50)
    user=models.ForeignKey(User)
    blacklist_words = models.TextField(blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.first_name


class BlackListedWords(models.Model):
    word = models.CharField(max_length=100)
    user = models.ForeignKey(FacebookUser)

    def __str__(self):
        return self.word


class DeletedComments(models.Model):
    # We store deleted comments and related metadata.
    message = models.TextField()
    message_by = models.CharField(max_length=200)
    user = models.ForeignKey(FacebookUser)
    message_id = models.CharField(max_length=100)

    def __str__(self):
        return self.message[:20]
