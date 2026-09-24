USE constructor_security;

INSERT INTO students
(student_number, first_name, last_name, email)
VALUES
('CU001', 'Thando', 'Mthembu', 'thando.mthembu@constructor.university'),
('CU002', 'Sarah', 'Meyer', 'sarah.meyer@constructor.university'),
('CU003', 'Daniel', 'Smith', 'daniel.smith@constructor.university');

INSERT INTO courses
(course_code, course_name)
VALUES
('CS101', 'Introduction to Computer Science'),
('CS201', 'Data Structures and Algorithms'),
('EC101', 'Introduction to Economics');

INSERT INTO enrolments
(student_id, course_id, enrolment_date)
VALUES
(1, 1, '2026-09-01'),
(1, 2, '2026-09-01'),
(2, 1, '2026-09-01'),
(3, 3, '2026-09-01');

INSERT INTO grades
(enrolment_id, grade)
VALUES
(1, 85.00),
(2, 78.00),
(3, 91.00),
(4, 73.00);