from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from csvimporter.models import CSVImporter

class ImportCSVViewTests(TestCase):

    def setUp(self):
        # usuario de prueba
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = Client()
        self.url = reverse("import_csv")

    def test_redirect_if_not_logged_in(self):
        """Unauthenticated users must be redirected to the login"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_get_form_logged_in(self):
        """Authenticated users should see the form"""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "import_form.html")
        self.assertContains(response, "<form")

    def test_upload_valid_csv(self):
        """A valid CSV upload creates records in the database."""
        self.client.login(username="testuser", password="testpass")
        csv_content = b"ID,Name,Year,Tv Certificate,Duration per episode,Genre,Ratings,Actor/Actress,Votes\n1,Movie1,2020,PG,30 min,Action,8.5,Actor1,1000"
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        response = self.client.post(self.url, {"file": csv_file})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "import_results.html")
        self.assertEqual(CSVImporter.objects.count(), 1)
        self.assertContains(response, "Successful uploads: 1")

    def test_upload_non_csv_file(self):
        """Uploading a file that is not CSV should return an error."""
        self.client.login(username="testuser", password="testpass")
        non_csv = SimpleUploadedFile("test.txt", b"Not a CSV", content_type="text/plain")
        response = self.client.post(self.url, {"file": non_csv})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "import_results.html")
        self.assertEqual(CSVImporter.objects.count(), 0)
        self.assertContains(response, "uploaded file is not an CSV")

    def test_upload_csv_with_invalid_columns(self):
        """CSV files with different columns are ignored and do not break the app."""
        self.client.login(username="testuser", password="testpass")
        csv_content = b"Foo,Bar,Baz\n1,2,3"
        csv_file = SimpleUploadedFile("bad.csv", csv_content, content_type="text/csv")
        response = self.client.post(self.url, {"file": csv_file})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "import_results.html")
        self.assertEqual(CSVImporter.objects.count(), 0)
        self.assertContains(response, "Import results")
