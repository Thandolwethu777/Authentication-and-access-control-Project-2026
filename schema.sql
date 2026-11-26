-- University portal schema. Flask verifies password hashes in app_users.
-- MariaDB PARSEC authenticates the application database connection (configured separately).
CREATE DATABASE IF NOT EXISTS constructor_security;
USE constructor_security;

CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS enrolments (
    enrolment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrolment_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE IF NOT EXISTS grades (
    grade_id INT PRIMARY KEY AUTO_INCREMENT,
    enrolment_id INT NOT NULL,
    grade DECIMAL(5,2) CHECK (grade BETWEEN 0 AND 100),
    FOREIGN KEY (enrolment_id) REFERENCES enrolments(enrolment_id)
);

CREATE TABLE IF NOT EXISTS lecturers (
    lecturer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS app_users (
    app_user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    user_role ENUM('student', 'lecturer', 'admin') NOT NULL,
    student_id INT NULL,
    lecturer_id INT NULL,
    password_hash VARCHAR(255) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_user_student FOREIGN KEY (student_id) REFERENCES students(student_id),
    CONSTRAINT fk_app_user_lecturer FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id),
    CONSTRAINT chk_app_user_identity CHECK (
        (user_role = 'student' AND student_id IS NOT NULL AND lecturer_id IS NULL)
        OR (user_role = 'lecturer' AND lecturer_id IS NOT NULL AND student_id IS NULL)
        OR (user_role = 'admin' AND student_id IS NULL AND lecturer_id IS NULL)
    )
);

-- Natural keys prevent duplicate registrations and multiple final grades.
-- On older installations these additions fail visibly if existing rows conflict.
ALTER TABLE enrolments ADD UNIQUE INDEX IF NOT EXISTS uq_registration (student_id, course_id);
ALTER TABLE grades ADD UNIQUE INDEX IF NOT EXISTS uq_final_grade (enrolment_id);
CREATE TABLE IF NOT EXISTS course_lecturers (
    course_id INT NOT NULL,
    lecturer_id INT NOT NULL,
    PRIMARY KEY (course_id, lecturer_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id)
);
