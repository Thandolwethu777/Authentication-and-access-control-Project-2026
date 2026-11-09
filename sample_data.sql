-- Re-runnable fictional demonstration data. Does not overwrite existing records.
USE constructor_security;

INSERT IGNORE INTO students (student_number, first_name, last_name, email) VALUES
('CU001', 'Thando', 'Mthembu', 'thando.mthembu@constructor.university'),
('CU002', 'Sarah', 'Meyer', 'sarah.meyer@constructor.university'),
('CU003', 'Daniel', 'Smith', 'daniel.smith@constructor.university');

INSERT IGNORE INTO courses (course_code, course_name) VALUES
('CS101', 'Introduction to Computer Science'),
('CS201', 'Data Structures and Algorithms'),
('EC101', 'Introduction to Economics');

INSERT IGNORE INTO lecturers (first_name, last_name, email, department) VALUES
('Maria', 'Schmidt', 'maria.schmidt@example.com', 'Computer Science'),
('James', 'Johnson', 'james.johnson@example.com', 'Computer Science'),
('Anna', 'Muller', 'anna.muller@example.com', 'Economics');

-- Resolve IDs by natural keys rather than assuming AUTO_INCREMENT starts at 1.
INSERT INTO enrolments (student_id, course_id, enrolment_date)
SELECT s.student_id, c.course_id, '2026-09-01'
FROM (
    SELECT 'CU001' AS student_number, 'CS101' AS course_code UNION ALL
    SELECT 'CU001', 'CS201' UNION ALL
    SELECT 'CU002', 'CS101' UNION ALL
    SELECT 'CU003', 'EC101'
) AS requested
JOIN students s ON s.student_number = requested.student_number
JOIN courses c ON c.course_code = requested.course_code
WHERE NOT EXISTS (
    SELECT 1 FROM enrolments e
    WHERE e.student_id = s.student_id AND e.course_id = c.course_id
);

INSERT INTO grades (enrolment_id, grade)
SELECT e.enrolment_id, requested.grade
FROM (
    SELECT 'CU001' AS student_number, 'CS101' AS course_code, 85.00 AS grade UNION ALL
    SELECT 'CU001', 'CS201', 78.00 UNION ALL
    SELECT 'CU002', 'CS101', 91.00 UNION ALL
    SELECT 'CU003', 'EC101', 73.00
) AS requested
JOIN students s ON s.student_number = requested.student_number
JOIN courses c ON c.course_code = requested.course_code
JOIN enrolments e ON e.student_id = s.student_id AND e.course_id = c.course_id
WHERE NOT EXISTS (
    SELECT 1 FROM grades g WHERE g.enrolment_id = e.enrolment_id
);

-- These are Flask website accounts, NOT MariaDB login accounts.
-- Password hashes are assigned locally by scripts/seed_demo_users.py.
INSERT INTO app_users (username, email, user_role, student_id, lecturer_id)
SELECT 'student1', 'thando@example.com', 'student', s.student_id, NULL
FROM students s WHERE s.student_number = 'CU001'
  AND NOT EXISTS (SELECT 1 FROM app_users a WHERE a.username = 'student1');

INSERT INTO app_users (username, email, user_role, student_id, lecturer_id)
SELECT 'student2', 'sarah@example.com', 'student', s.student_id, NULL
FROM students s WHERE s.student_number = 'CU002'
  AND NOT EXISTS (SELECT 1 FROM app_users a WHERE a.username = 'student2');

INSERT INTO app_users (username, email, user_role, student_id, lecturer_id)
SELECT 'lecturer1', 'maria.schmidt@example.com', 'lecturer', NULL, l.lecturer_id
FROM lecturers l WHERE l.email = 'maria.schmidt@example.com'
  AND NOT EXISTS (SELECT 1 FROM app_users a WHERE a.username = 'lecturer1');

INSERT INTO app_users (username, email, user_role, student_id, lecturer_id)
SELECT 'admin1', 'admin@example.com', 'admin', NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM app_users a WHERE a.username = 'admin1');
