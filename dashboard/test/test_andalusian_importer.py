from django.test import TestCase

from dashboard import andalusian_importer, release_importer


class AndalusianImporterTest(TestCase):
    fixtures = ["andalusian_instrument"]

    def test_get_instrument(self):
        importer = andalusian_importer.AndalusianReleaseImporter(None)
        instrument = importer._get_instrument("tar")
        self.assertIsNotNone(instrument)

        with self.assertRaisesMessage(release_importer.ImportFailedException, "Instrument lead vocals not found"):
            importer._get_instrument("lead vocals")

    def test_get_orchestra_performances(self):
        data = [
            {
                "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821",
                "type": "member of band",
                "target": "02568992-bca1-4310-a7cb-4c376c7cea6e",
                "direction": "backward",
                "attribute-list": ["viola"],
                "artist": {
                    "id": "02568992-bca1-4310-a7cb-4c376c7cea6e",
                    "name": "احمد البردعي",
                    "sort-name": "El Berdai, Ahmed",
                },
                "attributes": [{"attribute": "viola"}],
            },
            {
                "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821",
                "type": "member of band",
                "target": "04f3585f-3f9f-4966-8e19-75da8cf73808",
                "direction": "backward",
                "attribute-list": ["tar"],
                "artist": {
                    "id": "04f3585f-3f9f-4966-8e19-75da8cf73808",
                    "name": "عبد السلام العمراني بوخبزة",
                    "sort-name": "بوخبزة, عبد السلام العمراني",
                },
                "attributes": [{"attribute": "tar"}],
            },
            {
                "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821",
                "type": "member of band",
                "target": "1b5d9044-94e8-4866-b2c8-994305d8b5b9",
                "direction": "backward",
                "attribute-list": ["double bass"],
                "artist": {
                    "id": "1b5d9044-94e8-4866-b2c8-994305d8b5b9",
                    "name": "محمد الخلوف",
                    "sort-name": "Khalouf, Mohamed",
                },
                "attributes": [{"attribute": "double bass"}],
            },
            {
                "type": "member of band",
                "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821",
                "target": "2070a017-96e1-45aa-817a-9ecab2286ab4",
                "direction": "backward",
                "attribute-list": ["rebab"],
                "artist": {
                    "id": "2070a017-96e1-45aa-817a-9ecab2286ab4",
                    "name": "أنس العطار",
                    "sort-name": "أنس العطار",
                },
                "attributes": [{"attribute": "rebab"}],
            },
            {
                "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821",
                "type": "member of band",
                "target": "20dc0a1d-9d54-4344-a6af-60e11606a89b",
                "direction": "backward",
                "attribute-list": ["lead vocals"],
                "artist": {
                    "id": "20dc0a1d-9d54-4344-a6af-60e11606a89b",
                    "name": "رضا الطنيبر",
                    "sort-name": "الطنيبر, رضا",
                },
                "attributes": [{"attribute": "lead vocals"}],
            },
        ]

        importer = andalusian_importer.AndalusianReleaseImporter(None)
        performances = importer._get_orchestra_performances(data)
        expected = [
            ("02568992-bca1-4310-a7cb-4c376c7cea6e", ["viola"]),
            ("04f3585f-3f9f-4966-8e19-75da8cf73808", ["tar"]),
            ("1b5d9044-94e8-4866-b2c8-994305d8b5b9", ["double bass"]),
            ("2070a017-96e1-45aa-817a-9ecab2286ab4", ["rebab"]),
            ("20dc0a1d-9d54-4344-a6af-60e11606a89b", ["voice"]),
        ]
        self.assertEqual(performances, expected)
