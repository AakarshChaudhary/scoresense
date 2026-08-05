from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # so matplotlib works without a GUI
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

CSV_FILE = 'students.csv'
GRAPH_FOLDER = 'static/graphs'
SUBJECTS = ['Physics', 'Chemistry', 'Maths', 'English', 'IP']
CSV_COLUMNS = ['Name', 'RollNo'] + SUBJECTS


def ensure_csv_schema():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(CSV_FILE, index=False)
        return

    df = pd.read_csv(CSV_FILE, dtype={'RollNo': str})
    changed = False

    for column in CSV_COLUMNS:
        if column not in df.columns:
            df[column] = 0.0 if column in SUBJECTS else ''
            changed = True

    ordered_columns = CSV_COLUMNS + [column for column in df.columns if column not in CSV_COLUMNS]
    if changed or list(df.columns) != ordered_columns:
        df = df[ordered_columns]
        df.to_csv(CSV_FILE, index=False)


def load_students():
    ensure_csv_schema()
    df = pd.read_csv(CSV_FILE, dtype={'RollNo': str})
    df['RollNo'] = df['RollNo'].fillna('').astype(str)
    for subject in SUBJECTS:
        df[subject] = pd.to_numeric(df[subject], errors='coerce').fillna(0)
    return df


ensure_csv_schema()

# create graphs folder if it does not exist
if not os.path.exists(GRAPH_FOLDER):
    os.makedirs(GRAPH_FOLDER)


# calculates total, percentage and grade for one student
def calculate_result(student):
    total = sum(float(student[subject]) for subject in SUBJECTS)
    percentage = total / len(SUBJECTS)
    if percentage >= 90:
        grade = 'A+'
    elif percentage >= 75:
        grade = 'A'
    elif percentage >= 60:
        grade = 'B'
    elif percentage >= 40:
        grade = 'C'
    else:
        grade = 'Fail'
    return total, percentage, grade


def build_student_result(row):
    total, percentage, grade = calculate_result(row)
    result = {
        'Name': row['Name'],
        'RollNo': row['RollNo'],
        'Total': total,
        'Percentage': round(percentage, 2),
        'Grade': grade
    }
    for subject in SUBJECTS:
        result[subject] = row[subject]
    return result

# home page - shows quick stats and feature cards
@app.route('/')
def index():
    df = load_students()

    if df.empty:
        stats = {'total_students': 0, 'avg_percentage': 0, 'pass_percentage': 0}
    else:
        # calculate percentage for each student
        df['Percentage'] = df[SUBJECTS].sum(axis=1) / len(SUBJECTS)
        total_students = len(df)
        avg_percentage = round(df['Percentage'].mean(), 1)
        pass_count = (df['Percentage'] >= 40).sum()
        pass_percentage = round((pass_count / total_students) * 100, 1)
        stats = {
            'total_students': total_students,
            'avg_percentage': avg_percentage,
            'pass_percentage': pass_percentage
        }

    return render_template('index.html', stats=stats)


# add student form page
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # get form data
        name = request.form['name']
        roll_no = request.form['roll_no']

        # read existing data
        df = load_students()

        # add new row
        new_student = {'Name': name, 'RollNo': roll_no}
        for subject in SUBJECTS:
            new_student[subject] = float(request.form[subject.lower()])
        new_row = pd.DataFrame([new_student])
        df = pd.concat([df, new_row], ignore_index=True)

        # save back to csv
        df.to_csv(CSV_FILE, index=False)

        return redirect(url_for('view_students'))

    return render_template('add_student.html', subjects=SUBJECTS)


# view all students with calculated result columns
@app.route('/students')
def view_students():
    df = load_students()

    # add total, percentage, grade columns for display
    results = [build_student_result(row) for _, row in df.iterrows()]

    return render_template('view_students.html', students=results, subjects=SUBJECTS)


# search student by name or roll no
@app.route('/search', methods=['GET', 'POST'])
def search():
    matches = []
    if request.method == 'POST':
        query = request.form['query'].strip().lower()
        df = load_students()

        # filter rows where name or roll no matches the query
        df['RollNo'] = df['RollNo'].astype(str)
        df['Name'] = df['Name'].astype(str)
        filtered = df[
            df['Name'].str.lower().str.contains(query) |
            df['RollNo'].str.lower().str.contains(query)
        ]

        matches = [build_student_result(row) for _, row in filtered.iterrows()]

    return render_template('search.html', students=matches, subjects=SUBJECTS)


# generate all 4 graphs and show analysis page
@app.route('/analysis')
def analysis():
    df = load_students()

    if df.empty:
        return render_template('analysis.html', has_data=False)

    # calculate total marks per student for pass/fail and progress charts
    df['Total'] = df[SUBJECTS].sum(axis=1)
    df['Percentage'] = df['Total'] / len(SUBJECTS)

    # 1. subject wise average marks - bar chart
    plt.figure(figsize=(6, 4))
    subject_avg = [df[subject].mean() for subject in SUBJECTS]
    plt.bar(SUBJECTS, subject_avg, color=['#4F46E5', '#7C3AED', '#A78BFA', '#0EA5E9', '#10B981'])
    plt.title('Subject Wise Average Marks')
    plt.ylabel('Average Marks')
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/subject_avg.png')
    plt.close()

    # 2. topper comparison - bar chart of top 5 students by total marks
    top_students = df.sort_values('Total', ascending=False).head(5)
    plt.figure(figsize=(7, 4))
    plt.bar(top_students['Name'], top_students['Total'], color='#9C27B0')
    plt.title('Topper Comparison (Top 5)')
    plt.ylabel('Total Marks')
    plt.xticks(rotation=30, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/toppers.png')
    plt.close()

    # 3. pass/fail pie chart (pass = percentage >= 40)
    pass_count = (df['Percentage'] >= 40).sum()
    fail_count = (df['Percentage'] < 40).sum()
    plt.figure(figsize=(5, 5))
    plt.pie([pass_count, fail_count], labels=['Pass', 'Fail'], colors=['#4F46E5', '#F43F5E'], autopct='%1.1f%%')
    plt.title('Pass / Fail Ratio')
    plt.savefig(f'{GRAPH_FOLDER}/pass_fail.png')
    plt.close()

    # 4. student progress bar chart - percentage of every student
    plt.figure(figsize=(12, 5))  # wider figure to fit more names
    plt.bar(df['Name'], df['Percentage'], color='#7C3AED')
    plt.title('Student Wise Percentage')
    plt.ylabel('Percentage')
    plt.xticks(rotation=45, ha='right', fontsize=8)  # angled + right-aligned + smaller font
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/progress.png')
    plt.close()

    return render_template('analysis.html', has_data=True)


if __name__ == '__main__':
    app.run(debug=True, port=5050)
