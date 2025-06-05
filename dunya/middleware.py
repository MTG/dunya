import data.models
from data import utils


class ShowBootlegMiddleware:
    """A middleware to say if the current user is able to see
    restricted releases and recordings.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        permission = utils.get_user_permissions(request.user)
        request.permission = permission
        # TODO: remove the following lines after refactor
        user = request.user
        if user.is_staff:
            show_bootlegs = True
        else:
            show_bootlegs = False
        request.show_bootlegs = show_bootlegs

        response = self.get_response(request)
        return response
