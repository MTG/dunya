def get_user_permissions(user):
    permission = ["U"]
    if user.is_staff:
        permission = ["S", "R", "U"]
    elif user.has_perm('access_restricted'):
        permission = ["R", "U"]
    return permission
