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