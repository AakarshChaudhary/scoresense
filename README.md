# Student Performance Analytics Portal — Code Explanation

A web application built with **Flask (Python)** that stores student marks in a CSV file, displays them in dashboards, and generates performance graphs using **Matplotlib**.

---

## 1. Tech Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Flask | Web framework — handles routes/URLs and renders HTML pages |
| Pandas | Reads/writes the CSV file and performs calculations (averages, filtering, sorting) |
| Matplotlib | Generates the graphs as PNG images |
| HTML + Jinja2 | Templates — Jinja2 is Flask's templating engine, lets us use `{{ }}` and `{% %}` inside HTML |
| CSS | Styling (single file: `static/style.css`) |
| CSV | Acts as our "database" — no SQL database is used |

---

## 2. Folder Structure

```
student_portal/
├── app.py                   → main Flask application (all backend logic/routes)
├── students.csv               → stores all student data (our "database")
├── static/
│   ├── style.css              → all CSS styling
│   └── graphs/                 → auto-generated PNG graphs saved here
└── templates/
    ├── base.html               → common layout (header, nav bar) — other pages extend this
    ├── index.html               → home page (stats + feature cards)
    ├── add_student.html          → form to add a new student
    ├── view_students.html         → table showing all students + results
    ├── search.html                → search form + results table
    └── analysis.html               → displays the 4 graphs
```

---

## 3. `app.py` — Backend Logic

### Imports and Setup
- `Flask` creates the web server and defines routes (URLs).
- `pandas` (as `pd`) reads and writes `students.csv` like a spreadsheet.
- `matplotlib.use('Agg')` tells Matplotlib to generate images without opening a graphical window — needed because Flask runs in the background, not on a desktop screen.

### Startup Checks
- Checks if `students.csv` already exists. If not, creates one with just the column headers (`Name, RollNo, Physics, Chemistry, Maths`).
- Checks if the `static/graphs` folder exists, and creates it if missing — this is where graph images get saved.

### `calculate_result()` Function
Takes Physics, Chemistry, Maths marks as input and returns:
- `Total` = sum of all 3 subjects
- `Percentage` = Total ÷ 3
- `Grade` = decided using if/elif conditions on percentage:
  - 90+ → A+, 75+ → A, 60+ → B, 40+ → C, below 40 → Fail

This function is reused across multiple routes (Home, View All, Search) so the grading logic isn't repeated.

### Routes (URLs)

**`/` (Home Page)**
- Reads the full CSV into a DataFrame.
- Calculates 3 quick stats: total number of students, class average percentage, and pass rate (percentage of students scoring ≥ 40%).
- Passes these stats to `index.html` to display on the dashboard, along with feature cards linking to the other pages.

**`/add` (Add Student) — GET and POST**
- GET request shows the empty form.
- POST request:
  1. `request.form['name']` etc. reads the submitted form values.
  2. `pd.read_csv()` loads the existing data into a DataFrame.
  3. A new row is built and added using `pd.concat()`.
  4. `df.to_csv()` saves the updated table back to the file.
  5. `redirect()` sends the user to the View All page.

**`/students` (View All)**
- Reads the whole CSV.
- Loops through each row, calling `calculate_result()` to get Total/Percentage/Grade.
- Passes the combined data to `view_students.html` to render as a table.

**`/search` (Search) — GET and POST**
- POST request reads the search text from the form.
- Converts both the search text and the data to lowercase (case-insensitive matching).
- Uses `.str.contains()` from pandas to filter rows where Name or Roll No matches the query.
- Matching rows go through `calculate_result()` before being displayed.

**`/analysis` (Performance Analysis)**
- Reads the full CSV.
- Generates 4 graphs using Matplotlib, each following the same pattern:
  1. `plt.figure()` — creates a new blank chart
  2. Chart-specific drawing code (`plt.bar()` or `plt.pie()`)
  3. `plt.title()` / `plt.ylabel()` — add labels
  4. `plt.savefig()` — saves the chart as a PNG file inside `static/graphs/`
  5. `plt.close()` — clears the chart from memory so the next graph doesn't overlap

The 4 graphs:
- **Subject-wise Average** — bar chart of average marks per subject (`df['Physics'].mean()` etc.)
- **Topper Comparison** — bar chart of the top 5 students by total marks (`sort_values()` + `head(5)`)
- **Pass/Fail Pie Chart** — counts students with percentage ≥ 40 as Pass, rest as Fail
- **Student Progress** — bar chart showing every student's percentage

---

## 4. Templates (HTML Files)

- **`base.html`** is the parent template — contains the gradient header and navigation bar, plus a `{% block content %}` placeholder. Every other page extends this using `{% extends 'base.html' %}` and fills in only its own content, avoiding repeated header/nav code.

- **Jinja2 syntax used:**
  - `{{ variable }}` → prints a Python value inside HTML
  - `{% for s in students %} ... {% endfor %}` → loops through data (used to build table rows and feature cards)
  - `{% if condition %} ... {% endif %}` → conditional display (e.g. "no data" message on the analysis page)

- **`index.html`** — hero heading, a row of 3 stat cards (Total Students, Class Average, Pass Rate), and a 2×2 grid of feature cards linking to Add, View All, Search, and Analysis.

- **`add_student.html`** — a simple form with 5 input fields (Name, Roll No, Physics, Chemistry, Maths) that POSTs to `/add`.

- **`view_students.html`** and **`search.html`** — both render a table with the same columns (Name, Roll No, Physics, Chemistry, Maths, Total, Percentage, Grade), looping through the data passed from `app.py`.

- **`analysis.html`** — displays the 4 saved PNG graphs using `<img>` tags pointing to `static/graphs/`.

---

## 5. `static/style.css`

One CSS file styles the entire site, linked in `base.html` using `<link rel="stylesheet">`, so it applies to every page automatically.

- **Fonts:** Poppins for headings, Inter for body text (imported from Google Fonts).
- **Color theme:** Indigo-to-violet gradient (`#4F46E5` → `#7C3AED`) used for the header, stat cards, buttons, and hover states.
- **Layout:** `.container` centers page content in a white rounded card with a soft shadow. `.stats` and `.features` use CSS Flexbox/Grid to arrange the home page's stat cards and feature cards.
- **Tables:** Clean borders, uppercase column headers, subtle row hover highlight.
- **Forms:** Rounded input fields with a focus border color matching the theme.

---

## 6. How the Pieces Fit Together

1. `app.py` is the single entry point — it defines all routes and connects them to templates.
2. Every route reads/writes `students.csv` through pandas instead of a database.
3. Templates only handle *display* — all calculations (totals, percentages, grades, stats, graph data) happen in `app.py`, keeping the HTML simple.
4. `base.html` + CSS give a consistent look across all pages without repeating code.
5. Matplotlib graphs are generated on-demand each time `/analysis` is visited, saved as image files, and displayed like any other image on the page.