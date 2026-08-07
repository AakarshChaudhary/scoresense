from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib

# This lets Matplotlib save graph images without opening a separate window.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


app = Flask(__name__)

# File and folder names used by this project.
CSV_FILE = 'students.csv'
GRAPH_FOLDER = 'static/graphs'

# These are the columns that should exist in students.csv.
CSV_COLUMNS = ['Name', 'RollNo', 'Physics', 'Chemistry', 'Maths', 'English', 'IP']


def prepare_project_files():
    """Create the CSV file and graph folder if they are missing."""
    if not os.path.exists(CSV_FILE):
        empty_table = pd.DataFrame(columns=CSV_COLUMNS)
        empty_table.to_csv(CSV_FILE, index=False)

    if not os.path.exists(GRAPH_FOLDER):
        os.makedirs(GRAPH_FOLDER)


def read_students():
    """Read students.csv and return it as a table."""
    students = pd.read_csv(CSV_FILE, dtype={'RollNo': str})

    # If an older CSV file is missing a column, add that column.
    file_changed = False
    for column in CSV_COLUMNS:
        if column not in students.columns:
            students[column] = 0
            file_changed = True

    # Keep the columns in the same order every time.
    students = students[CSV_COLUMNS]

    # Roll numbers are text, not numbers, so 01112 stays 01112.
    students['RollNo'] = students['RollNo'].fillna('').astype(str)

    # Marks should always be numbers. Empty or invalid marks become 0.
    students['Physics'] = pd.to_numeric(students['Physics'], errors='coerce').fillna(0)
    students['Chemistry'] = pd.to_numeric(students['Chemistry'], errors='coerce').fillna(0)
    students['Maths'] = pd.to_numeric(students['Maths'], errors='coerce').fillna(0)
    students['English'] = pd.to_numeric(students['English'], errors='coerce').fillna(0)
    students['IP'] = pd.to_numeric(students['IP'], errors='coerce').fillna(0)

    if file_changed:
        students.to_csv(CSV_FILE, index=False)

    return students


def calculate_result(physics, chemistry, maths, english, ip_marks):
    """Calculate total marks, percentage, and grade for one student."""
    total = physics + chemistry + maths + english + ip_marks
    percentage = total / 5

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


def make_student_result(row):
    """Add Total, Percentage, and Grade to one student's row."""
    total, percentage, grade = calculate_result(
        row['Physics'],
        row['Chemistry'],
        row['Maths'],
        row['English'],
        row['IP']
    )

    return {
        'Name': row['Name'],
        'RollNo': row['RollNo'],
        'Physics': row['Physics'],
        'Chemistry': row['Chemistry'],
        'Maths': row['Maths'],
        'English': row['English'],
        'IP': row['IP'],
        'Total': total,
        'Percentage': round(percentage, 2),
        'Grade': grade
    }


prepare_project_files()


# Home page: shows total students, class average, and pass rate.
@app.route('/')
def index():
    students = read_students()

    if len(students) == 0:
        total_students = 0
        average_percentage = 0
        pass_percentage = 0
    else:
        students['Total'] = (
            students['Physics'] +
            students['Chemistry'] +
            students['Maths'] +
            students['English'] +
            students['IP']
        )
        students['Percentage'] = students['Total'] / 5

        total_students = len(students)
        average_percentage = round(students['Percentage'].mean(), 1)
        pass_count = len(students[students['Percentage'] >= 40])
        pass_percentage = round((pass_count / total_students) * 100, 1)

    stats = {
        'total_students': total_students,
        'avg_percentage': average_percentage,
        'pass_percentage': pass_percentage
    }

    return render_template('index.html', stats=stats)


# Add student page: shows a form and saves the submitted marks.
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        physics = float(request.form['physics'])
        chemistry = float(request.form['chemistry'])
        maths = float(request.form['maths'])
        english = float(request.form['english'])
        ip_marks = float(request.form['ip'])

        students = read_students()

        new_student = pd.DataFrame([{
            'Name': name,
            'RollNo': roll_no,
            'Physics': physics,
            'Chemistry': chemistry,
            'Maths': maths,
            'English': english,
            'IP': ip_marks
        }])

        students = pd.concat([students, new_student], ignore_index=True)
        students.to_csv(CSV_FILE, index=False)

        return redirect(url_for('view_students'))

    return render_template('add_student.html')


# View all page: displays every student with total, percentage, and grade.
@app.route('/students')
def view_students():
    students = read_students()
    student_results = []

    for _, row in students.iterrows():
        student_results.append(make_student_result(row))

    return render_template('view_students.html', students=student_results)


# Search page: finds students by name or roll number.
@app.route('/search', methods=['GET', 'POST'])
def search():
    student_results = []

    if request.method == 'POST':
        search_text = request.form['query'].strip().lower()
        students = read_students()

        students['Name'] = students['Name'].astype(str)
        students['RollNo'] = students['RollNo'].astype(str)

        name_matches = students['Name'].str.lower().str.contains(search_text, regex=False)
        roll_matches = students['RollNo'].str.lower().str.contains(search_text, regex=False)
        matching_students = students[name_matches | roll_matches]

        for _, row in matching_students.iterrows():
            student_results.append(make_student_result(row))

    return render_template('search.html', students=student_results)


# Analysis page: creates graphs and shows them on the page.
@app.route('/analysis')
def analysis():
    students = read_students()

    if len(students) == 0:
        return render_template('analysis.html', has_data=False)

    students['Total'] = (
        students['Physics'] +
        students['Chemistry'] +
        students['Maths'] +
        students['English'] +
        students['IP']
    )
    students['Percentage'] = students['Total'] / 5

    # 1. Subject-wise average marks graph.
    subject_names = ['Physics', 'Chemistry', 'Maths', 'English', 'IP']
    subject_averages = [
        students['Physics'].mean(),
        students['Chemistry'].mean(),
        students['Maths'].mean(),
        students['English'].mean(),
        students['IP'].mean()
    ]

    plt.figure(figsize=(6, 4))
    plt.bar(subject_names, subject_averages, color=['#4F46E5', '#7C3AED', '#A78BFA', '#0EA5E9', '#10B981'])
    plt.title('Subject Wise Average Marks')
    plt.ylabel('Average Marks')
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/subject_avg.png')
    plt.close()

    # 2. Top 5 students by total marks.
    top_students = students.sort_values('Total', ascending=False).head(5)

    plt.figure(figsize=(7, 4))
    plt.bar(top_students['Name'], top_students['Total'], color='#9C27B0')
    plt.title('Topper Comparison (Top 5)')
    plt.ylabel('Total Marks')
    plt.xticks(rotation=30, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/toppers.png')
    plt.close()

    # 3. Pass/fail ratio.
    pass_count = len(students[students['Percentage'] >= 40])
    fail_count = len(students[students['Percentage'] < 40])
    pass_percentage = round((pass_count / len(students)) * 100, 1)

    plt.figure(figsize=(4.5, 4.5))
    plt.pie(
        [pass_count, fail_count],
        colors=['#2D6A4F', '#E11D48'],
        startangle=90,
        autopct='%1.1f%%',
        pctdistance=0.78,
        wedgeprops={'width': 0.38, 'edgecolor': 'white', 'linewidth': 3}
    )
    plt.text(0, 0.05, f'{pass_percentage}%', ha='center', va='center', fontsize=20, fontweight='bold')
    plt.text(0, -0.14, 'Pass Rate', ha='center', va='center', fontsize=11, color='#64748B')
    plt.title('Pass / Fail Ratio')
    plt.legend([f'Pass: {pass_count}', f'Fail: {fail_count}'], loc='lower center', bbox_to_anchor=(0.5, -0.08), ncol=2)
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/pass_fail.png', bbox_inches='tight')
    plt.close()

    # 4. Percentage of every student.
    plt.figure(figsize=(12, 5))
    plt.bar(students['Name'], students['Percentage'], color='#7C3AED')
    plt.title('Student Wise Percentage')
    plt.ylabel('Percentage')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/progress.png')
    plt.close()

    return render_template('analysis.html', has_data=True)


if __name__ == '__main__':
    app.run(debug=True, port=5050)
