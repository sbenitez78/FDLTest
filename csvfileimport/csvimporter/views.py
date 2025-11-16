import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.files.base import ContentFile

from .forms import UploadCSVFile
from .models import CSVImporter
from .utils import upload_image_to_s3

MODEL_FIELDS = [
    'csv_id',
    'name',
    'year',
    'tv_certificate',
    'duration_per_episode',
    'genre',
    'rating',
    'actors',
    'votes'
]

@login_required
def import_csv(request):
    results = {"total": 0, "success": 0, "failed": 0, "errors": []}

    if request.method == "POST":
        form = UploadCSVFile(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            image_file = request.FILES.get("image")  # optional image in form

            if not csv_file.name.endswith('.csv'):
                results["errors"].append("uploaded file is not an CSV")
                results["failed"] += 1
                return render(request, "import_results.html", {"results": results})

            # manual image upload (form)
            s3_manual_url = None
            if image_file:
                try:
                    s3_manual_url = upload_image_to_s3(
                        image_file.name,
                        ContentFile(image_file.read()),  # Convertimos a archivo en memoria
                        from_url=False
                    )
                except Exception as e:
                    results["errors"].append(f"Manual image upload failed: {e}")

            try:
                df = pd.read_csv(csv_file)

                lower_fields = [f.lower() for f in MODEL_FIELDS] #prevent errors of a different csv #test with the Books csv to test errors
                df = df[[col for col in df.columns if col.lower() in lower_fields]]

                for i, row in enumerate(df.to_dict(orient='records'), start=1):
                    results["total"] += 1
                    try:
                        rating = None
                        votes = None
                        image_url = s3_manual_url  # manual upload by default

                        # image upload from CSV url
                        if 'Image URL' in row and row['Image URL']:
                            try:
                                file_name = f"{row.get('ID') or 'row'}_{row.get('Name','')}.jpg"
                                image_url = upload_image_to_s3(file_name, row['Image URL'])
                            except Exception as e:
                                results["errors"].append(f"Image upload failed for row {i}: {e}")

                        if 'Ratings' in row and pd.notna(row['Ratings']):
                            try:
                                rating = float(row['Ratings'])
                            except:
                                rating = None

                        if 'Votes' in row and pd.notna(row['Votes']):
                            try:
                                votes = int(str(row['Votes']).replace(",", "").strip())
                            except:
                                votes = None

                        CSVImporter.objects.create(
                            csv_id=row.get("ID") or None,
                            name=row.get("Name", ""),
                            year=row.get("Year", ""),
                            tv_certificate=row.get("Tv Certificate", ""),
                            duration_per_episode=row.get("Duration per episode", ""),
                            genre=row.get("Genre", ""),
                            rating=rating,
                            actors=row.get("Actor/Actress", ""),
                            votes=votes,
                            image_url=image_url,
                        )

                        results["success"] += 1

                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Line {i}: {e}")

                return render(request, "import_results.html", {"results": results})

            except Exception as e:
                results["errors"].append(f"Error processing CSV: {e}")
                results["failed"] += 1
                return render(request, "import_results.html", {"results": results})

    else:
        form = UploadCSVFile()

    return render(request, "import_form.html", {"form": form})

def account_logout(request):
    logout(request)
    return redirect('/import')