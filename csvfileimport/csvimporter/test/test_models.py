from django.test import TestCase
from csvimporter.models import CSVImporter

class ModelTest(TestCase):

    def test_model_creation(self):
        item = CSVImporter.objects.create(
            csv_id=5,
            name="Test Show",
            year="2021",
            rating=8.1,
            votes=1000
        )

        self.assertEqual(str(item.name), "Test Show")
        self.assertEqual(item.votes, 1000)
