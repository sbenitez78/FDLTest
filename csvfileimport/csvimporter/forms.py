from django import forms
from . import models

class UploadCSVFile(forms.Form):
    file = forms.FileField()
    image = forms.FileField(label="Optional image", required=False)  # opcional

    