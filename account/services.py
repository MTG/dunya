from django.contrib.auth.models import Group, User

RESTRICTED_GROUP_NAME = "Can view restricted items"


def add_user_to_restricted_group(user: User):
    """Add a user to the restricted group that gives access to some special docserver collections."""
    group = Group.objects.get_by_natural_key(RESTRICTED_GROUP_NAME)
    user.groups.add(group)
