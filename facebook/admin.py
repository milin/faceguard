from django.contrib import admin

from facebook.models import (
    FacebookUser,
    BlackListedWords
)


# Register your models here.
admin.site.register(FacebookUser)
admin.site.register(BlackListedWords)
