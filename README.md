# Student Performance Analytics Portal

This project is a simple Flask app for storing student marks, calculating results, and showing charts.

It is a good beginner project because each part has one clear job.

## What the app does

- Add a new student with marks
- View all students in a table
- Search by name or roll number
- Calculate total, percentage, and grade
- Show graphs for class performance

## Main files

- app.py: the main Python code for Flask routes and logic
- students.csv: the data file that stores student records
- templates/: the HTML pages shown in the browser
- static/: CSS and graph images

## Very simple flow

1. The user opens a page such as /students.
2. Flask finds the matching function in app.py.
3. The function reads the CSV file.
4. Python calculates the required result.
5. Flask sends the data to an HTML page.
6. The browser shows the final page.

## How marks are calculated

For each student:

- Total = Physics + Chemistry + Maths + English + IP
- Percentage = Total / 5

Grades:

- 90 or above = A+
- 75 or above = A
- 60 or above = B
- 40 or above = C
- Below 40 = Fail

## Beginner-friendly explanation for viva

If someone asks, "What does this project do?", you can say:

> This project is a student marks management system. It stores student data in a CSV file, calculates results, and displays them on a web page. The app uses Flask to handle web pages and Pandas to work with the student data.

If someone asks, "How is the code organized?", you can say:

> The main logic is in app.py. There are small functions for reading data, adding results, and creating graphs. Each route handles one page such as home, add student, view students, or analysis.

## Run the app

Install the requirements first, then run:

```powershell
python app.py
```

Open this in the browser:

```text
http://127.0.0.1:5050
```
