from django.core.management.base import BaseCommand, CommandError

from facebook.lib import delete_black_listed_comments


class Command(BaseCommand):
    help = "Management command to delete facebook comments having blacklisted words"

    def handle(self, *args, **options):
        delete_black_listed_comments()
