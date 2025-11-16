# FDLTest
Python/Django Developer 8-Hour Trial Task

Technical decisions
LEVEL 1 
- I created a project within a venv for package management. This keeps project dependencies isolated, avoids conflicts with other Django versions or packages, and allows each project to have its own libraries. It makes deploying and reproducing the project easier. Taking into account the job requirements, the database engine was changed to PostgreSQL.
- I used the Kaggle platform to download two sample dataset for import. One about movies called Thriller, Crime, Action and another about books called Goodreads-books.
- I decided to use pandas for data formatting because I find it easy to handle missing values, dynamic columns, filtering, and data cleaning compared to the classic csv.reader import method that reads each row as a list instead of a dictionary, and I need to know the column order and access it by index, making it less readable... indexes have to be managed manually. 

Please, for this to work, use [[**AllThrillerSeriesList.csv**](www.kaggle.com/datasets/jealousleopard/goodreadsbooks?resource=download)], as that's how the model is set up. To generate an error and see the message, use [[**books.csv**](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks?resource=download)].

LEVEL 2
- I used the django-allauth library because it has a wide variety of login systems. I used Google as the provider to have the opportunity to implement some GCP.

IMPORTANT: The URI is configured as http://127.0.0.1:8000/accounts/google/login/callback/ - if the Docker host is different, it may cause authentication problems.

- The secret and ID data are set in the .env file. This file will be sent via email for best practices.

- If you encounter difficulties starting the Dockerfile, I've added a check so you can use the .env file directly using `decouple` without needing to use os.environment variables.

- The design of this login still needs improvement. It is currently functional.

- I implemented unit tests to test how the form, model, and views are working so far.

- A video will be uploaded demonstrating the functionality up to this point.

LEVEL 3

- A major area for improvement is adding more robust validation for image uploads. Currently, I find the validation process weak and prone to errors.

- Another area for improvement is that when an image is uploaded, the URL is saved for all records.

--- 

## What was the creation process and how did I get it up and running locally? (Brief Summary)

- Project creation with `python django-admin startproject csvfileimport` for the core and addition of `appstart csvimporter`.
- Creation of a virtual environment for installing dependencies (see requirements.txt).
- Creation of an .env file for use.
- Configurations in settings.py
- After completing the model creation, execution of `python manage.py makemigrations` and `python manage.py migrate` to create the database.

- Verify in pgAdmin that the table creation was correct. It was necessary to create a database named FDLTest beforehand (later automated with Docker).

- Creation of views for CSV import and display of results.

- Implementation of OAuth with Google. It was necessary to migrate models again for user insertion during registration. Registration is now possible.

- Completion of unit tests and update of the README.

- To execute test you can use `python manage.py` test command 

Video too large to upload so here is a drive URL to see it: https://drive.google.com/file/d/1PKxxMUaQbjZ_tuV0K-SAMOtf7uS3zTCc/view?usp=sharing