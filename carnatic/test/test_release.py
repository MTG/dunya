from django.test import TestCase
from django.contrib import auth

from carnatic.models import Concert
import data

class ReleaseTest(TestCase):
    def test_performers(self):
        """ Who is a performer on a release
            - People who are in the release's artist list
            - People who are perfomers on a track """
        pass

class ReleaseViewsTest(TestCase):
    fixtures = ['initial_data', ]

    def setUp(self):
        self.user1 = auth.models.User.objects.create_user("user1", "", "pass1")
        self.user1.is_staff = True
        self.user1.save()
        self.user2 = auth.models.User.objects.create_user("user2", "", "pass2")

        self.rel1 = Concert.objects.create(mbid="d89a53a7-ad04-4608-9328-9de2d38dae85", title="Carnatic Instrumental - Violin", bootleg=False)
        self.rel1.source = data.models.Source.objects.create(title="xx", uri="http://musicbrainz.org/release/d89a53a7-ad04-4608-9328-9de2d38dae85", source_name=data.models.SourceName.objects.get(name="MusicBrainz"))
        self.rel1.save()
        self.rel2 = Concert.objects.create(mbid="692f0429-ad82-4d98-ae99-debbd17defa3", title="Alathur Brothers concert", bootleg=True)
        self.rel2.source = data.models.Source.objects.create(title="xx", uri="http://musicbrainz.org/release/692f0429-ad82-4d98-ae99-debbd17defa3", source_name=data.models.SourceName.objects.get(name="MusicBrainz"))
        self.rel2.save()

    def test_bootleg_not_loggedin(self):
        self.client.logout()
        r = self.client.get("/carnatic/concert/692f0429-ad82-4d98-ae99-debbd17defa3")
        self.assertEqual(404, r.status_code)

    def test_bootleg_not_staff(self):
        self.client.login(username="user2", password="pass2")
        r = self.client.get("/carnatic/concert/692f0429-ad82-4d98-ae99-debbd17defa3")
        self.assertEqual(404, r.status_code)

    def test_bootleg_staff(self):
        self.client.login(username="user1", password="pass1")
        r = self.client.get("/carnatic/concert/692f0429-ad82-4d98-ae99-debbd17defa3")
        self.assertEqual(True, r.context["bootleg"])

    def test_normal_not_loggedin(self):
        self.client.logout()
        r = self.client.get("/carnatic/concert/d89a53a7-ad04-4608-9328-9de2d38dae85")
        self.assertEqual(False, r.context["bootleg"])

    def test_normal_not_staff(self):
        self.client.login(username="user2", password="pass2")
        r = self.client.get("/carnatic/concert/d89a53a7-ad04-4608-9328-9de2d38dae85")
        self.assertEqual(False, r.context["bootleg"])

