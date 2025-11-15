import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadCSVFile
from .models import CSVImporter
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

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

            if not csv_file.name.endswith('.csv'):
                results["errors"].append("uploaded file is not an CSV")
                results["failed"] += 1
                return render(request, "import_results.html", {"results": results})

            try:
                df = pd.read_csv(csv_file)

                lower_fields = [f.lower() for f in MODEL_FIELDS] #prevent errors of a different csv #test with the Books csv to test errors
                df = df[[col for col in df.columns if col.lower() in lower_fields]]

                for i, row in enumerate(df.to_dict(orient='records'), start=1):
                    results["total"] += 1
                    try:
                        rating = None
                        votes = None
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
                            votes=votes
                        )

                        results["success"] += 1

                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Line {i}: {e}")

                return render(request, "import_results.html", {"results": results})

            except Exception as e:
                results["errors"].append(f"Error processig CSV: {e}")
                results["failed"] += 1
                return render(request, "import_results.html", {"results": results})

    else:
        form = UploadCSVFile()

    return render(request, "import_form.html", {"form": form})

def account_logout(request):
    logout(request)
    return redirect('/import')