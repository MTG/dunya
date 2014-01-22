from data import models

class PageLoggerMiddleware(object):

    def process_request(self, request):
        path = request.get_full_path()
        user = request.user
        if user.is_authenticated():
            uname = user.username
        else:
            uname = None
        ip = request.META["REMOTE_ADDR"]
        models.VisitLog.objects.create(user=uname, ip=ip, path=path)

        # Continue processing
        return None

