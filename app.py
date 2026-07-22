from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # so matplotlib works without a GUI
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

CSV_FILE = 'students.csv'
GRAPH_FOLDER = 'static/graphs'

# create csv with headers if it does not exist yet
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=['Name', 'RollNo', 'Physics', 'Chemistry', 'Maths'])
    df.to_csv(CSV_FILE, index=False)

# create graphs folder if it does not exist
if not os.path.exists(GRAPH_FOLDER):
    os.makedirs(GRAPH_FOLDER)


# calculates total, percentage and grade for one student
def calculate_result(physics, chemistry, maths):
    total = physics + chemistry + maths
    percentage = total / 3
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

# home page - shows quick stats and feature cards
@app.route('/')
def index():
    df = pd.read_csv(CSV_FILE)

    if df.empty:
        stats = {'total_students': 0, 'avg_percentage': 0, 'pass_percentage': 0}
    else:
        # calculate percentage for each student
        df['Percentage'] = (df['Physics'] + df['Chemistry'] + df['Maths']) / 3
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
        physics = float(request.form['physics'])
        chemistry = float(request.form['chemistry'])
        maths = float(request.form['maths'])

        # read existing data
        df = pd.read_csv(CSV_FILE)

        # add new row
        new_row = pd.DataFrame([{
            'Name': name, 'RollNo': roll_no,
            'Physics': physics, 'Chemistry': chemistry, 'Maths': maths
        }])
        df = pd.concat([df, new_row], ignore_index=True)

        # save back to csv
        df.to_csv(CSV_FILE, index=False)

        return redirect(url_for('view_students'))

    return render_template('add_student.html')


# view all students with calculated result columns
@app.route('/students')
def view_students():
    df = pd.read_csv(CSV_FILE)

    # add total, percentage, grade columns for display
    results = []
    for _, row in df.iterrows():
        total, percentage, grade = calculate_result(row['Physics'], row['Chemistry'], row['Maths'])
        results.append({
            'Name': row['Name'], 'RollNo': row['RollNo'],
            'Physics': row['Physics'], 'Chemistry': row['Chemistry'], 'Maths': row['Maths'],
            'Total': total, 'Percentage': round(percentage, 2), 'Grade': grade
        })

    return render_template('view_students.html', students=results)


# search student by name or roll no
@app.route('/search', methods=['GET', 'POST'])
def search():
    matches = []
    if request.method == 'POST':
        query = request.form['query'].strip().lower()
        df = pd.read_csv(CSV_FILE)

        # filter rows where name or roll no matches the query
        df['RollNo'] = df['RollNo'].astype(str)
        filtered = df[
            df['Name'].str.lower().str.contains(query) |
            df['RollNo'].str.lower().str.contains(query)
        ]

        for _, row in filtered.iterrows():
            total, percentage, grade = calculate_result(row['Physics'], row['Chemistry'], row['Maths'])
            matches.append({
                'Name': row['Name'], 'RollNo': row['RollNo'],
                'Physics': row['Physics'], 'Chemistry': row['Chemistry'], 'Maths': row['Maths'],
                'Total': total, 'Percentage': round(percentage, 2), 'Grade': grade
            })

    return render_template('search.html', students=matches)


# generate all 4 graphs and show analysis page
@app.route('/analysis')
def analysis():
    df = pd.read_csv(CSV_FILE)

    if df.empty:
        return render_template('analysis.html', has_data=False)

    # calculate total marks per student for pass/fail and progress charts
    df['Total'] = df['Physics'] + df['Chemistry'] + df['Maths']
    df['Percentage'] = df['Total'] / 3

    # 1. subject wise average marks - bar chart
    plt.figure(figsize=(6, 4))
    subject_avg = [df['Physics'].mean(), df['Chemistry'].mean(), df['Maths'].mean()]
    plt.bar(['Physics', 'Chemistry', 'Maths'], subject_avg, color=['#4F46E5', '#7C3AED', '#A78BFA'])
    plt.title('Subject Wise Average Marks')
    plt.ylabel('Average Marks')
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