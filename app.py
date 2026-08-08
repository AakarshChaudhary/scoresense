from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib

# This lets Matplotlib save graph images without opening a separate window.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


app = Flask(__name__)

# Simple project settings.
CSV_FILE = 'students.csv'
GRAPH_FOLDER = 'static/graphs'
CSV_COLUMNS = ['Name', 'RollNo', 'Physics', 'Chemistry', 'Maths', 'English', 'IP']
SUBJECT_COLUMNS = ['Physics', 'Chemistry', 'Maths', 'English', 'IP']


def prepare_project_files():
    """Create the CSV file and graph folder if they are missing."""
    if not os.path.exists(CSV_FILE):
        empty_table = pd.DataFrame(columns=CSV_COLUMNS)
        empty_table.to_csv(CSV_FILE, index=False)

    if not os.path.exists(GRAPH_FOLDER):
        os.makedirs(GRAPH_FOLDER)


def read_students():
    """Read the CSV file and make sure the data is clean and ready to use."""
    students = pd.read_csv(CSV_FILE, dtype={'RollNo': str})

    # Add any missing columns so the file stays consistent.
    for column in CSV_COLUMNS:
        if column not in students.columns:
            students[column] = 0

    students = students[CSV_COLUMNS]
    students['RollNo'] = students['RollNo'].fillna('').astype(str)

    # Convert marks to numbers. Empty values become 0.
    for subject in SUBJECT_COLUMNS:
        students[subject] = pd.to_numeric(students[subject], errors='coerce').fillna(0)

    students.to_csv(CSV_FILE, index=False)
    return students


def get_grade(percentage):
    """Return the grade for a percentage value."""
    if percentage >= 90:
        return 'A+'
    if percentage >= 75:
        return 'A'
    if percentage >= 60:
        return 'B'
    if percentage >= 40:
        return 'C'
    return 'Fail'


def add_result_columns(students):
    """Add Total, Percentage, and Grade to the student table."""
    students_with_results = students.copy()
    students_with_results['Total'] = students_with_results[SUBJECT_COLUMNS].sum(axis=1)
    students_with_results['Percentage'] = students_with_results['Total'] / len(SUBJECT_COLUMNS)
    students_with_results['Grade'] = students_with_results['Percentage'].apply(get_grade)
    return students_with_results


def build_student_results(students):
    """Convert each row into a simple dictionary for the HTML page."""
    student_results = []
    for _, row in students.iterrows():
        student_results.append({
            'Name': row['Name'],
            'RollNo': row['RollNo'],
            'Physics': row['Physics'],
            'Chemistry': row['Chemistry'],
            'Maths': row['Maths'],
            'English': row['English'],
            'IP': row['IP'],
            'Total': row['Total'],
            'Percentage': round(row['Percentage'], 2),
            'Grade': row['Grade']
        })

    return student_results


def calculate_class_stats(students):
    """Create simple statistics for the home page."""
    if students.empty:
        return {
            'total_students': 0,
            'avg_percentage': 0,
            'pass_percentage': 0
        }

    total_students = len(students)
    average_percentage = round(students['Percentage'].mean(), 1)
    pass_count = int((students['Percentage'] >= 40).sum())
    pass_percentage = round((pass_count / total_students) * 100, 1)

    return {
        'total_students': total_students,
        'avg_percentage': average_percentage,
        'pass_percentage': pass_percentage
    }


def create_analysis_graphs(students):
    """Create and save the graphs used on the analysis page."""
    subject_averages = [students[subject].mean() for subject in SUBJECT_COLUMNS]

    plt.figure(figsize=(6, 4))
    plt.bar(SUBJECT_COLUMNS, subject_averages, color=['#4F46E5', '#7C3AED', '#A78BFA', '#0EA5E9', '#10B981'])
    plt.title('Subject Wise Average Marks')
    plt.ylabel('Average Marks')
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/subject_avg.png')
    plt.close()

    top_students = students.sort_values('Total', ascending=False).head(5)

    plt.figure(figsize=(7, 4))
    plt.bar(top_students['Name'], top_students['Total'], color='#9C27B0')
    plt.title('Topper Comparison (Top 5)')
    plt.ylabel('Total Marks')
    plt.xticks(rotation=30, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/toppers.png')
    plt.close()

    pass_count = int((students['Percentage'] >= 40).sum())
    fail_count = int((students['Percentage'] < 40).sum())
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

    plt.figure(figsize=(12, 5))
    plt.bar(students['Name'], students['Percentage'], color='#7C3AED')
    plt.title('Student Wise Percentage')
    plt.ylabel('Percentage')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    plt.savefig(f'{GRAPH_FOLDER}/progress.png')
    plt.close()


prepare_project_files()


@app.route('/')
def index():
    """Show the home page with simple class statistics."""
    students = add_result_columns(read_students())
    stats = calculate_class_stats(students)
    return render_template('index.html', stats=stats)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """Show the form and save a new student record."""
    if request.method == 'POST':
        new_student = {
            'Name': request.form['name'],
            'RollNo': request.form['roll_no'],
            'Physics': float(request.form['physics']),
            'Chemistry': float(request.form['chemistry']),
            'Maths': float(request.form['maths']),
            'English': float(request.form['english']),
            'IP': float(request.form['ip'])
        }

        students = read_students()
        students.loc[len(students)] = new_student
        students.to_csv(CSV_FILE, index=False)

        return redirect(url_for('view_students'))

    return render_template('add_student.html')


@app.route('/students')
def view_students():
    """Show all students with their results and ranking."""
    search_text = request.args.get('query', '').strip().lower()
    students = add_result_columns(read_students())
    student_results = build_student_results(students)

    if student_results:
        percentages = [student['Percentage'] for student in student_results]
        total_students = len(percentages)

        for student in student_results:
            students_below_or_equal = sum(1 for value in percentages if value <= student['Percentage'])
            student['Percentile'] = round((students_below_or_equal / total_students) * 100, 2)

        student_results.sort(key=lambda student: student['Percentage'], reverse=True)

        for index, student in enumerate(student_results, start=1):
            student['Rank'] = index

    if search_text:
        student_results = [
            student for student in student_results
            if search_text in str(student['Name']).lower() or search_text in str(student['RollNo']).lower()
        ]

    return render_template('view_students.html', students=student_results, query=search_text)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """Keep the older search URL working."""
    if request.method == 'POST':
        return redirect(url_for('view_students', query=request.form['query'].strip()))

    return redirect(url_for('view_students'))


@app.route('/analysis')
def analysis():
    """Create graphs and show them on the analysis page."""
    students = add_result_columns(read_students())

    if students.empty:
        return render_template('analysis.html', has_data=False)

    create_analysis_graphs(students)
    return render_template('analysis.html', has_data=True)


if __name__ == '__main__':
    app.run(debug=True, port=5050)
