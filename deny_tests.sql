
-- Test MariaDB GRANT, ROLE and DENY functionality.
-- The tests demonstrate that users can access permitted
-- database tables but are blocked from restricted operations.

-- IMPORTANT:
-- 1. Run each test in the correct HeidiSQL session.
-- 2. Execute queries ONE AT A TIME.
-- 3. Access-denied errors are EXPECTED for restricted queries.
-- 4. Do not run restricted-user tests as MariaDB ADMIN.

-- SECTION 1: VERIFY ROLE CONFIGURATION
-- SESSION: MariaDB ADMIN
-- Check the MariaDB version.
SELECT VERSION();

-- Check permissions for the demonstration role.
-- Expected:
-- GRANT SELECT ON constructor_security.*
-- DENY SELECT ON constructor_security.app_users
SHOW GRANTS FOR portal_demo_role;

-- Check permissions for the real student role.
-- Expected: DENY SELECT on app_users
-- and DENY UPDATE, DELETE on grades.
SHOW GRANTS FOR student_role;

-- Check permissions for the real lecturer role.
-- Expected: DENY SELECT on app_users
-- and DENY DELETE on grades.
SHOW GRANTS FOR lecturer_role;

-- Check administrator permissions.
SHOW GRANTS FOR admin_role;


-- SECTION 2: DEMONSTRATION ROLE TEST
-- SESSION: DENY TEST
-- USER: deny_test

-- Verify the authenticated account and active role.
-- Expected role: portal_demo_role
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


