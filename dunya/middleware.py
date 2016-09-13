from django.conf import settings
import data.models
from data import utils

class PageLoggerMiddleware(object):

    def process_request(self, request):
        path = request.get_full_path()
        user = request.user
        if user.is_authenticated():
            uname = user.username
        else:
            uname = None
        ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
        data.models.VisitLog.objects.create(user=uname, ip=ip, path=path)

        # Continue processing
        return None

class ShowBootlegMiddleware(object):
    """ A middleware to say if the current user is able to see
        restricted releases and recordings.
    """

    def process_request(self, request):
        permission = utils.get_user_permissions(request.user)
        request.permission = permission
        # remove the following lines after refactor
        user = request.user
        if user.is_staff:
            show_bootlegs = True
        else:
            show_bootlegs = False
        request.show_bootlegs = show_bootlegs

        # Continue processing
        return None
