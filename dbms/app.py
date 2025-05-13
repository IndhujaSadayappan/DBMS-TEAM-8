from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask import render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Change this to a proper secret key
app.secret_key = 'your_secret_key'

# Database connection details
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'python'
app.config['MYSQL_DB'] = 'counselling_system'

# Initialize MySQL
mysql = MySQL(app)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Student signup route
@app.route('/student/signup', methods=['GET', 'POST'])
def student_signup():
    msg = ''
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        dob = request.form['dob']
        gender = request.form['gender']
        category = request.form['category']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        twelfth_mark = request.form['twelfth_mark']
        password = request.form['password']
        
        # Create cursor
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if email already exists
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Name must contain only characters and numbers!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Hash the password
            hashed_password = generate_password_hash(password)
            
            # Insert into users table
            cursor.execute('INSERT INTO users (email, password, role) VALUES (%s, %s, %s)', 
                          (email, hashed_password, 'student'))
            mysql.connection.commit()
            
            # Get the user ID
            cursor.execute('SELECT userid FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            user_id = user['userid']
            
            # Insert into students table
            cursor.execute('''
                INSERT INTO students (userid, name, dob, gender, category, email, phone, address, twelfth_mark) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, name, dob, gender, category, email, phone, address, twelfth_mark))
            mysql.connection.commit()
            
            msg = 'You have successfully registered!'
            return redirect(url_for('student_login'))
    
    return render_template('student_signup.html', msg=msg)

# Student login route
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND role = %s', (email, 'student'))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['userid']
            session['email'] = user['email']
            session['role'] = user['role']
            
            return redirect(url_for('student_dashboard'))
        else:
            msg = 'Incorrect email/password!'
    
    return render_template('student_login.html', msg=msg)

# Admin signup route
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (email, password, role, name) VALUES (%s, %s, %s, %s)', 
                          (email, hashed_password, 'admin', name))
            mysql.connection.commit()
            msg = 'You have successfully registered as an admin!'
            return redirect(url_for('admin_login'))
    
    return render_template('admin_signup.html', msg=msg)

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND role = %s', (email, 'admin'))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['userid']
            session['email'] = user['email']
            session['role'] = user['role']
            
            return redirect(url_for('admin_dashboard'))
        else:
            msg = 'Incorrect email/password!'
    
    return render_template('admin_login.html', msg=msg)

@app.route('/student/dashboard')
def student_dashboard():
    if 'loggedin' in session and session['role'] == 'student':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT * FROM students WHERE userid = %s', (session['id'],))
        student = cursor.fetchone()
        
        cursor.execute('SELECT * FROM colleges')
        colleges = cursor.fetchall()
        
        cursor.execute('SELECT c.*, col.name as college_name FROM courses c JOIN colleges col ON c.college_id = col.college_id')
        courses = cursor.fetchall()
        
        cursor.execute('''
            SELECT p.college_id, p.course_id, p.preference_order, 
                   c.name as college_name, co.name as course_name 
            FROM preferences p 
            JOIN colleges c ON p.college_id = c.college_id 
            JOIN courses co ON p.course_id = co.course_id 
            WHERE p.student_id = %s 
            ORDER BY p.preference_order
        ''', (session['id'],))
        preferences = cursor.fetchall()

        from collections import defaultdict
        college_courses_map = defaultdict(list)
        for course in courses:
            college_courses_map[course['college_id']].append(course)
        
        college_courses_map = dict(college_courses_map)  # safely convert here

        return render_template('student_dashboard.html',
                               student=student,
                               colleges=colleges,
                               preferences=preferences,
                               college_courses_map=college_courses_map)

    return redirect(url_for('student_login'))


# Save student preferences
@app.route('/student/save_preferences', methods=['POST'])
def save_preferences():
    if 'loggedin' in session and session['role'] == 'student':
        preferences = request.form.getlist('preferences[]')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Delete existing preferences
        cursor.execute('DELETE FROM preferences WHERE student_id = %s', (session['id'],))
        mysql.connection.commit()
        
        # Save new preferences
        for i, pref in enumerate(preferences):
            college_id, course_id = pref.split('_')
            cursor.execute('''
                INSERT INTO preferences (student_id, college_id, course_id, preference_order) 
                VALUES (%s, %s, %s, %s)
            ''', (session['id'], college_id, course_id, i+1))
        
        mysql.connection.commit()
        flash('Preferences saved successfully!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return redirect(url_for('student_login'))

# Admin dashboard
from datetime import datetime

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get all colleges
        cursor.execute('SELECT * FROM colleges')
        colleges = cursor.fetchall()
        
        # Get all courses
        cursor.execute('SELECT c.*, col.name as college_name FROM courses c JOIN colleges col ON c.college_id = col.college_id')
        courses = cursor.fetchall()
        
        # Get all counselling sessions
        cursor.execute('SELECT * FROM counselling_sessions')
        sessions = cursor.fetchall()
        
        # Get student count
        cursor.execute('SELECT COUNT(*) as count FROM students')
        student_count = cursor.fetchone()['count']
        
        # Get preference count
        cursor.execute('SELECT COUNT(*) as count FROM preferences')
        preference_count = cursor.fetchone()['count']
        
        # Get allotment count
        cursor.execute('SELECT COUNT(*) as count FROM allotments')
        allotment_count = cursor.fetchone()['count']
        
        # Get current date (as date object, not datetime)
        now = datetime.now().date()
        
        return render_template('admin_dashboard.html', 
                              colleges=colleges, 
                              courses=courses, 
                              sessions=sessions, 
                              student_count=student_count,
                              preference_count=preference_count,
                              allotment_count=allotment_count,
                              now=now)  # Pass `now` as a date object
    
    return redirect(url_for('admin_login'))


# Add college
@app.route('/admin/add_college', methods=['POST'])
def add_college():
    if 'loggedin' in session and session['role'] == 'admin':
        name = request.form['name']
        location = request.form['location']
        website = request.form['website']
        description = request.form['description']
        est_year = request.form['est_year']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            INSERT INTO colleges (name, location, website, description, est_year) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (name, location, website, description, est_year))
        mysql.connection.commit()
        
        flash('College added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('admin_login'))

# Add course
@app.route('/admin/add_course', methods=['POST'])
def add_course():
    if 'loggedin' in session and session['role'] == 'admin':
        name = request.form['name']
        duration = request.form['duration']
        department = request.form['department']
        college_id = request.form['college_id']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            INSERT INTO courses (name, duration, department, college_id) 
            VALUES (%s, %s, %s, %s)
        ''', (name, duration, department, college_id))
        mysql.connection.commit()
        
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('admin_login'))

# Add counselling session
@app.route('/admin/add_session', methods=['POST'])
def add_session():
    if 'loggedin' in session and session['role'] == 'admin':
        year = request.form['year']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        round_num = request.form['round']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            INSERT INTO counselling_sessions (year, start_date, end_date, round) 
            VALUES (%s, %s, %s, %s)
        ''', (year, start_date, end_date, round_num))
        mysql.connection.commit()
        
        flash('Counselling session added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('admin_login'))

# View student preferences
@app.route('/admin/view_preferences')
def view_preferences():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('''
            SELECT p.*, s.name as student_name, s.twelfth_mark, c.name as college_name, co.name as course_name 
            FROM preferences p 
            JOIN students s ON p.student_id = s.userid 
            JOIN colleges c ON p.college_id = c.college_id 
            JOIN courses co ON p.course_id = co.course_id 
            ORDER BY s.twelfth_mark DESC, p.preference_order
        ''')
        preferences = cursor.fetchall()
        
        return render_template('view_preferences.html', preferences=preferences)
    
    return redirect(url_for('admin_login'))

# Generate allotment
@app.route('/admin/generate_allotment')
def generate_allotment():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Clear existing allotments
        cursor.execute('DELETE FROM allotments')
        mysql.connection.commit()
        
        # Get all students ordered by marks (highest first)
        cursor.execute('SELECT * FROM students ORDER BY twelfth_mark DESC')
        students = cursor.fetchall()
        
        # Get all courses with capacity (assuming each course has capacity)
        cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
        
        # Create a dictionary to track course capacities (assuming 50 seats per course)
        course_capacity = {course['course_id']: 50 for course in courses}
        
        # Process each student
        for student in students:
            # Get student preferences
            cursor.execute('''
                SELECT * FROM preferences 
                WHERE student_id = %s 
                ORDER BY preference_order
            ''', (student['userid'],))
            preferences = cursor.fetchall()
            
            # Try to allocate based on preference order
            allocated = False
            for pref in preferences:
                course_id = pref['course_id']
                
                # Check if course has capacity
                if course_capacity[course_id] > 0:
                    # Allocate the course
                    cursor.execute('''
                        INSERT INTO allotments (student_id, college_id, course_id) 
                        VALUES (%s, %s, %s)
                    ''', (student['userid'], pref['college_id'], course_id))
                    
                    # Reduce capacity
                    course_capacity[course_id] -= 1
                    allocated = True
                    break
            
            # If no preference could be allocated, mark as unallocated
            if not allocated:
                cursor.execute('''
                    INSERT INTO allotments (student_id, college_id, course_id, status) 
                    VALUES (%s, %s, %s, %s)
                ''', (student['userid'], 0, 0, 'Not Allocated'))
        
        mysql.connection.commit()
        flash('Allotment generated successfully!', 'success')
        return redirect(url_for('view_allotments'))
    
    return redirect(url_for('admin_login'))

# View allotments
@app.route('/admin/view_allotments')
def view_allotments():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('''
            SELECT a.*, s.name as student_name, s.twelfth_mark, c.name as college_name, co.name as course_name 
            FROM allotments a 
            JOIN students s ON a.student_id = s.userid 
            LEFT JOIN colleges c ON a.college_id = c.college_id 
            LEFT JOIN courses co ON a.course_id = co.course_id 
            ORDER BY s.twelfth_mark DESC
        ''')
        allotments = cursor.fetchall()
        
        return render_template('view_allotments.html', allotments=allotments)
    
    return redirect(url_for('admin_login'))

# Student view allotment
@app.route('/student/view_allotment')
def student_view_allotment():
    if 'loggedin' in session and session['role'] == 'student':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('''
            SELECT a.*, c.name as college_name, co.name as course_name 
            FROM allotments a 
            LEFT JOIN colleges c ON a.college_id = c.college_id 
            LEFT JOIN courses co ON a.course_id = co.course_id 
            WHERE a.student_id = %s
        ''', (session['id'],))
        allotment = cursor.fetchone()
        
        return render_template('student_allotment.html', allotment=allotment)
    
    return redirect(url_for('student_login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('role', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

print("Flask application initialized successfully!")