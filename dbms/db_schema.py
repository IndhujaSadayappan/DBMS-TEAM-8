import MySQLdb

# Database connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'python'
DB_NAME = 'counselling_system'

# Connect to MySQL server
conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD)
cursor = conn.cursor()

# Create database if it doesn't exist
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.execute(f"USE {DB_NAME}")

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid INT UNIQUE,
    name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    category VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    twelfth_mark FLOAT NOT NULL,
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE
)
''')

# Create colleges table
cursor.execute('''
CREATE TABLE IF NOT EXISTS colleges (
    college_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    website VARCHAR(100),
    description TEXT,
    est_year INT
)
''')

# Create courses table
cursor.execute('''
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    duration VARCHAR(50) NOT NULL,
    department VARCHAR(100) NOT NULL,
    college_id INT NOT NULL,
    FOREIGN KEY (college_id) REFERENCES colleges(college_id) ON DELETE CASCADE
)
''')

# Create counselling_sessions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS counselling_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    round INT NOT NULL
)
''')

# Create preferences table
cursor.execute('''
CREATE TABLE IF NOT EXISTS preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    college_id INT NOT NULL,
    course_id INT NOT NULL,
    preference_order INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users(userid) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(college_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
)
''')

# Create allotments table
cursor.execute('''
CREATE TABLE IF NOT EXISTS allotments (
    allotment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    college_id INT NOT NULL,
    course_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'Allocated',
    allotment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(userid) ON DELETE CASCADE
)
''')

# Insert sample data for testing
# Sample colleges
cursor.execute('''
INSERT INTO colleges (name, location, website, description, est_year) VALUES
('Engineering College of Technology', 'Chennai', 'www.ect.edu', 'Premier engineering institution', 1950),
('National Institute of Science', 'Bangalore', 'www.nis.edu', 'Leading science and technology institute', 1960),
('University of Computer Applications', 'Hyderabad', 'www.uca.edu', 'Specialized in computer science education', 1985)
''')

# Sample courses
cursor.execute('''
INSERT INTO courses (name, duration, department, college_id) VALUES
('Computer Science Engineering', '4 years', 'Computer Science', 1),
('Electrical Engineering', '4 years', 'Electrical', 1),
('Mechanical Engineering', '4 years', 'Mechanical', 1),
('Information Technology', '4 years', 'IT', 2),
('Electronics and Communication', '4 years', 'ECE', 2),
('Civil Engineering', '4 years', 'Civil', 3),
('Artificial Intelligence', '4 years', 'AI', 3)
''')

# Sample counselling session
cursor.execute('''
INSERT INTO counselling_sessions (year, start_date, end_date, round) VALUES
(2023, '2023-06-01', '2023-06-15', 1)
''')

conn.commit()
conn.close()

print("Database schema created successfully!")