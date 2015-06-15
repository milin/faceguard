from facebook.models import (
    FacebookUser,
)

from facebook.views import Facebook


def delete_black_listed_comments():
    users = FacebookUser.objects.all()
    fb = Facebook()
    for user in users:
        fb.start_process(user)
