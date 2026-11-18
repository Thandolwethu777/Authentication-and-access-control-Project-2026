
SELECT VERSION();

SHOW GRANTS FOR portal_demo_role;

SHOW GRANTS FOR student_role;

SHOW GRANTS FOR lecturer_role;

SHOW GRANTS FOR admin_role;

SELECT CURRENT_USER(), CURRENT_ROLE();

-- TEST 1: ALLOWED
-- The demonstration role can read course information.
-- Expected: SUCCESS
SELECT * FROM constructor_security.courses;

-- TEST 2: DENIED
-- The demonstration role cannot read portal account data.
-- Expected: ACCESS DENIED
SELECT * FROM constructor_security.app_users;



-- SECTION 3: REAL STUDENT ROLE TEST
-- SESSION: STUDENT TEST
-- USER: student_deny_test
-- Verify the authenticated account and active role.
-- Expected role: student_role
SELECT CURRENT_USER(), CURRENT_ROLE();

-- TEST 3: ALLOWED
-- Students can view available courses.
-- Expected: SUCCESS
SELECT * FROM constructor_security.courses;

-- TEST 4: DENIED
-- Students cannot read portal account records.
-- Expected: ACCESS DENIED
SELECT * FROM constructor_security.app_users;

-- TEST 5: DENIED
-- Students cannot update grades.
-- Expected: ACCESS DENIED
-- WHERE 1 = 0 ensures no records can be changed.
UPDATE constructor_security.grades
SET grade = grade
WHERE 1 = 0;



-- SECTION 4: REAL LECTURER ROLE TEST
-- SESSION: LECTURER TEST
-- USER: lecturer_deny_test
-- Verify the authenticated account and active role.
-- Expected role: lecturer_role
SELECT CURRENT_USER(), CURRENT_ROLE();

-- TEST 6: ALLOWED
-- Lecturers can view available courses.
-- Expected: SUCCESS
SELECT * FROM constructor_security.courses;

-- TEST 7: DENIED
-- Lecturers cannot read portal account records.
-- Expected: ACCESS DENIED
SELECT * FROM constructor_security.app_users;

-- TEST 8: DENIED
-- Lecturers cannot delete student grades.
-- Expected: ACCESS DENIED
-- WHERE 1 = 0 ensures no records can be deleted.
DELETE FROM constructor_security.grades
WHERE 1 = 0;


