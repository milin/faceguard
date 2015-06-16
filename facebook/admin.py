from django.contrib import admin
from facebook.models import (
    BlackListedWords,
    FacebookUser,
    DeletedComments
)

class BlackListedWordsInline(admin.TabularInline):
        model = BlackListedWords

class DeletedCommentsInline(admin.TabularInline):
        model = DeletedComments

class FacebookUserAdmin(admin.ModelAdmin):
    inlines = [
        BlackListedWordsInline,
        DeletedCommentsInline
    ]

# Register your models here.
admin.site.register(FacebookUser, FacebookUserAdmin)
admin.site.register(BlackListedWords)
