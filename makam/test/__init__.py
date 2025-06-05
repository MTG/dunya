from django.db import connection


def setup():
    try:
        cursor = connection.cursor()
        cursor.execute("create extension unaccent")
    except Exception:
        pass
