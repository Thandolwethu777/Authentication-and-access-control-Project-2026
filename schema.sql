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
    grade DECIMAL(5,2),
    FOREIGN KEY (enrolment_id) REFERENCES enrolments(enrolment_id)
);
CREATE TABLE lecturers (
    lecturer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL
);


-- Portal login accounts
-- Authentication is handled by MariaDB PARSEC.
-- No passwords are stored in this table.

CREATE TABLE IF NOT EXISTS app_users (
    app_user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    user_role ENUM('student', 'lecturer', 'admin') NOT NULL,
    student_id INT NULL,
    lecturer_id INT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_app_user_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    CONSTRAINT fk_app_user_lecturer
        FOREIGN KEY (lecturer_id)
        REFERENCES lecturers(lecturer_id),

    CONSTRAINT chk_app_user_identity
        CHECK (
            (user_role = 'student'
                AND student_id IS NOT NULL
                AND lecturer_id IS NULL)
            OR
            (user_role = 'lecturer'
                AND lecturer_id IS NOT NULL
                AND student_id IS NULL)
            OR
            (user_role = 'admin'
                AND student_id IS NULL
                AND lecturer_id IS NULL)
        )
);

