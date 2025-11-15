from django.test import TestCase
from csvimporter.forms import UploadCSVFile
from django.core.files.uploadedfile import SimpleUploadedFile

class FormTest(TestCase):

    def test_form_valid(self):
        file = SimpleUploadedFile("file.csv", b"ID,Name\n1,Test")
        form = UploadCSVFile(files={"file": file})
        self.assertTrue(form.is_valid())
