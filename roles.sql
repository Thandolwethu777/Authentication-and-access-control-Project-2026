USE constructor_security;



-- STUDENT ROLE


CREATE ROLE student_role;

GRANT SELECT
ON constructor_security.students
TO student_role;

GRANT SELECT
ON constructor_security.courses
TO student_role;

GRANT SELECT
ON constructor_security.enrolments
TO student_role;

GRANT SELECT
ON constructor_security.grades
TO student_role;


-- LECTURER ROLE


CREATE ROLE lecturer_role;

GRANT SELECT
ON constructor_security.students
TO lecturer_role;

GRANT SELECT
ON constructor_security.courses
TO lecturer_role;

GRANT SELECT
ON constructor_security.enrolments
TO lecturer_role;

GRANT SELECT
ON constructor_security.grades
TO lecturer_role;

GRANT UPDATE
ON constructor_security.grades
TO lecturer_role;



-- ADMIN ROLE


CREATE ROLE admin_role;

GRANT ALL PRIVILEGES
ON constructor_security.*
TO admin_role;

-- Backend role for the Flask application
CREATE ROLE IF NOT EXISTS backend_role;

-- Read permissions
GRANT SELECT ON constructor_security.app_users TO backend_role;
GRANT SELECT ON constructor_security.students TO backend_role;
GRANT SELECT ON constructor_security.courses TO backend_role;
GRANT SELECT ON constructor_security.lecturers TO backend_role;
GRANT SELECT ON constructor_security.enrolments TO backend_role;

-- Grade management permissions
GRANT SELECT, INSERT, UPDATE ON constructor_security.grades TO backend_role;

-- Portal demonstration role
CREATE ROLE IF NOT EXISTS portal_demo_role;

GRANT SELECT ON constructor_security.*
TO portal_demo_role;
