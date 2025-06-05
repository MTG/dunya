from django.test import TestCase, RequestFactory
from rest_framework.exceptions import ValidationError

from dunya.api import get_collection_ids_from_request_or_error


class ApiTest(TestCase):
    def test_validate_one_uuid(self):
        factory = RequestFactory()
        get_request = factory.get("/", HTTP_DUNYA_COLLECTION="35671712-f6a8-449d-bad8-c8d7d94c84ba")

        uuids = get_collection_ids_from_request_or_error(get_request)
        self.assertEqual(uuids, ["35671712-f6a8-449d-bad8-c8d7d94c84ba"])

    def test_validate_many_uuids(self):
        factory = RequestFactory()
        get_request = factory.get(
            "/", HTTP_DUNYA_COLLECTION="35671712-f6a8-449d-bad8-c8d7d94c84ba,35671712-f6a8-449d-bad8-c8d7d94c84ba"
        )

        uuids = get_collection_ids_from_request_or_error(get_request)
        self.assertEqual(uuids, ["35671712-f6a8-449d-bad8-c8d7d94c84ba", "35671712-f6a8-449d-bad8-c8d7d94c84ba"])

    def test_validate_invalid_uuid(self):
        factory = RequestFactory()
        get_request = factory.get("/", HTTP_DUNYA_COLLECTION="x")

        try:
            get_collection_ids_from_request_or_error(get_request)
            self.fail("expected exception")
        except ValidationError:
            pass

    def test_validate_one_invalid_uuid(self):
        factory = RequestFactory()
        get_request = factory.get("/", HTTP_DUNYA_COLLECTION="35671712-f6a8-449d-bad8-c8d7d94c84ba,x")

        try:
            get_collection_ids_from_request_or_error(get_request)
            self.fail("expected exception")
        except ValidationError:
            pass
