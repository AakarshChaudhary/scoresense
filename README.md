# Student Performance Analytics Portal

This is a simple Flask web app for a school student marks project.

It stores student marks in `students.csv`, shows the records on web pages, calculates results, and creates graphs.

For virtual environment setup, read `VENV_SETUP.md`.

## What The App Does

- Add a student and their marks
- View all students
- Search by name or roll number
- Calculate total marks, percentage, and grade
- Show performance graphs

## Subjects Used

The project uses 5 subjects:

- Physics
- Chemistry
- Maths
- English
- IP

## Project Files

```text
app.py
students.csv
requirements.txt
VENV_SETUP.md
static/
  style.css
  graphs/
templates/
  base.html
  index.html
  add_student.html
  view_students.html
  search.html
  analysis.html
```

## What Each File Is For

`app.py`

This is the main Python file. It runs the Flask app, reads and writes `students.csv`, calculates results, and creates graphs.

`students.csv`

This is the student data file. It acts like a small database.

Columns:

```text
Name, RollNo, Physics, Chemistry, Maths, English, IP
```

`templates/`

This folder has the HTML pages shown in the browser.

`static/style.css`

This file controls the design, colors, spacing, tables, buttons, and cards.

`static/graphs/`

This folder stores graph images created by the app.

## How Marks Are Calculated

For each student:

```text
Total = Physics + Chemistry + Maths + English + IP
Percentage = Total / 5
```

Grades:

```text
90 or above = A+
75 or above = A
60 or above = B
40 or above = C
Below 40   = Fail
```

## Pages In The App

`/`

Home page. Shows total students, class average, and pass rate.

`/add`

Add Student page. Lets the user enter student details and marks.

`/students`

View All page. Shows all student records with total, percentage, and grade.

`/search`

Search page. Finds a student by name or roll number.

`/analysis`

Performance Analysis page. Shows graphs for the class.

## Simple Code Flow

1. The browser opens a page like `/students`.
2. Flask runs the matching function in `app.py`.
3. The function reads `students.csv`.
4. Python calculates the needed result.
5. Flask sends the data to an HTML file in `templates/`.
6. The browser displays the final page.

## Graphs Created

The Analysis page creates 4 graphs:

- Subject Wise Average Marks
- Topper Comparison
- Pass / Fail Ratio
- Student Wise Progress

## Run The App

After installing the requirements:

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5050
```
