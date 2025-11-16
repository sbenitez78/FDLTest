import boto3
from django.conf import settings
from urllib.request import urlopen
from io import BytesIO

def upload_image_to_s3(file_name, file_or_url, from_url=True):
    """
    file_name: nombre con el que se guardará en S3
    file_or_url: puede ser URL (str) o archivo en memoria (BytesIO / ContentFile)
    from_url: True si file_or_url es URL, False si es archivo subido manualmente
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    if from_url:
        response = urlopen(file_or_url)
        data = BytesIO(response.read())
    else:
        # file_or_url es un archivo en memoria
        data = file_or_url

    s3.upload_fileobj(
        data,
        settings.AWS_STORAGE_BUCKET_NAME,
        file_name
    )

    return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
