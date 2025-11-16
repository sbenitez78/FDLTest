from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from csvimporter.models import CSVImporter
from unittest.mock import patch

class ImportCSVViewTests(TestCase):

    def setUp(self):
        # usuario de prueba
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = Client()
        self.url = reverse("import_csv")

    # ----------------------
    # ACCESO Y LOGIN
    # ----------------------
    def test_redirect_if_not_logged_in(self):
        """Usuarios no autenticados deben ser redirigidos al login"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_get_form_logged_in(self):
        """Usuarios autenticados ven el formulario"""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "import_form.html")
        self.assertContains(response, "<form")

    # ----------------------
    # CSV VÁLIDO
    # ----------------------
    def test_upload_valid_csv(self):
        """Una subida de CSV válida crea registros en la DB"""
        self.client.login(username="testuser", password="testpass")
        csv_content = b"ID,Name,Year,Tv Certificate,Duration per episode,Genre,Ratings,Actor/Actress,Votes\n1,Movie1,2020,PG,30 min,Action,8.5,Actor1,1000"
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        response = self.client.post(self.url, {"file": csv_file})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "import_results.html")
        self.assertEqual(CSVImporter.objects.count(), 1)
        self.assertContains(response, "Successful uploads: 1")

    # ----------------------
    # CSV NO VÁLIDO / FORMATO
    # ----------------------
    def test_upload_non_csv_file(self):
        """Subir un archivo que no es CSV devuelve error"""
        self.client.login(username="testuser", password="testpass")
        non_csv = SimpleUploadedFile("test.txt", b"Not a CSV", content_type="text/plain")
        response = self.client.post(self.url, {"file": non_csv})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "import_results.html")
        self.assertEqual(CSVImporter.objects.count(), 0)
        self.assertContains(response, "uploaded file is not an CSV")

    def test_upload_csv_with_invalid_columns(self):
        """CSV con columnas incorrectas no rompe la app"""
        self.client.login(username="testuser", password="testpass")
        csv_content = b"Foo,Bar,Baz\n1,2,3"
        csv_file = SimpleUploadedFile("bad.csv", csv_content, content_type="text/csv")
        response = self.client.post(self.url, {"file": csv_file})
        self.assertEqual(CSVImporter.objects.count(), 0)
        self.assertContains(response, "Import results")

    # ----------------------
    # CSV CON MULTIPLES FILAS
    # ----------------------
    def test_upload_csv_multiple_rows(self):
        """CSV con varias filas se importa correctamente"""
        self.client.login(username="testuser", password="testpass")
        csv_content = b"ID,Name,Year,Tv Certificate,Duration per episode,Genre,Ratings,Actor/Actress,Votes\n1,Movie1,2020,PG,30 min,Action,8.5,Actor1,1000\n2,Movie2,2021,R,45 min,Drama,7.0,Actor2,500"
        csv_file = SimpleUploadedFile("multi.csv", csv_content, content_type="text/csv")
        response = self.client.post(self.url, {"file": csv_file})
        self.assertEqual(CSVImporter.objects.count(), 2)
        self.assertContains(response, "Successful uploads: 2")

    # ----------------------
    # CSV PARCIALMENTE INVÁLIDO
    # ----------------------
    def test_upload_csv_partial_invalid(self):
        """CSV con filas parcialmente inválidas"""
        self.client.login(username="testuser", password="testpass")
        csv_content = b"ID,Name,Year,Tv Certificate,Duration per episode,Genre,Ratings,Actor/Actress,Votes\n1,Movie1,2020,PG,30 min,Action,8.5,Actor1,1000\n2,,,,,,,,"
        csv_file = SimpleUploadedFile("partial.csv", csv_content, content_type="text/csv")
        response = self.client.post(self.url, {"file": csv_file})
        self.assertEqual(CSVImporter.objects.count(), 1)
        self.assertContains(response, "Successful uploads: 1")
        self.assertContains(response, "Failed uploads: 1")

    # ----------------------
    # SUBIDA DE IMÁGENES (MOCK S3)
    # ----------------------
    @patch("csvimporter.utils.upload_image_to_s3")
    def test_upload_image_called(self, mock_upload):
        """Se llama a la función de subida de S3 cuando hay imagen en CSV"""
        self.client.login(username="testuser", password="testpass")
        csv_content = b"ID,Name,Year,Tv Certificate,Duration per episode,Genre,Ratings,Actor/Actress,Votes,Image\n1,Movie1,2020,PG,30 min,Action,8.5,Actor1,1000,http://example.com/image.jpg"
        csv_file = SimpleUploadedFile("image.csv", csv_content, content_type="text/csv")
        mock_upload.return_value = "https://bucket.s3.amazonaws.com/image.jpg"
        response = self.client.post(self.url, {"file": csv_file})
        self.assertEqual(CSVImporter.objects.count(), 1)
        mock_upload.assert_called_once()

    @patch("csvimporter.utils.upload_image_to_s3")
    def test_upload_image_failure(self, mock_upload):
        """Si la subida de imagen falla, se muestra error en los resultados"""
        self.client.login(username="testuser", password="testpass")
        csv_content = b"ID,Name,Year,Tv Certificate,Duration per episode,Genre,Ratings,Actor/Actress,Votes,Image\n1,Movie1,2020,PG,30 min,Action,8.5,Actor1,1000,http://example.com/image.jpg"
        csv_file = SimpleUploadedFile("failimage.csv", csv_content, content_type="text/csv")
        mock_upload.side_effect = Exception("S3 upload failed")
        response = self.client.post(self.url, {"file": csv_file})
        self.assertContains(response, "Manual image upload failed: S3 upload failed")
