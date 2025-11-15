# FDLTest
Python/Django Developer 8-Hour Trial Task

Technical decisions
LEVEL 1 
- I created a project within a venv for package management. This keeps project dependencies isolated, avoids conflicts with other Django versions or packages, and allows each project to have its own libraries. It makes deploying and reproducing the project easier. Taking into account the job requirements, the database engine was changed to PostgreSQL.
- I used the Kaggle platform to download two sample dataset for import. One about movies called Thriller, Crime, Action and another about books called Goodreads-books.
- I decided to use pandas for data formatting because I find it easy to handle missing values, dynamic columns, filtering, and data cleaning compared to the classic csv.reader import method that reads each row as a list instead of a dictionary, and I need to know the column order and access it by index, making it less readable... indexes have to be managed manually. 

Please, for this to work, use **AllThrillerSeriesList.csv**, as that's how the model is set up. To generate an error and see the message, use **books.csv**.
