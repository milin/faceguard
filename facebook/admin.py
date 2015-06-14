from django.contrib import admin
from facebook.models import BlackListedWords, FacebookUser



class BlackListedWordsInline(admin.TabularInline):
        model = BlackListedWords

class FacebookUserAdmin(admin.ModelAdmin):
    inlines = [
        BlackListedWordsInline,
    ]

# Register your models here.
admin.site.register(FacebookUser, FacebookUserAdmin)
admin.site.register(BlackListedWords)
