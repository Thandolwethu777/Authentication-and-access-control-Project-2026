
USE constructor_security;

-- Students and lecturers must not read
-- portal account records directly.

DENY SELECT ON constructor_security.app_users
TO student_role;

DENY SELECT ON constructor_security.app_users
TO lecturer_role;

-- Students must not modify grades.
DENY UPDATE, DELETE ON constructor_security.grades
TO student_role;

-- Lecturers may update grades under the existing
-- policy, but must never delete grade records.
DENY DELETE ON constructor_security.grades
TO lecturer_role;
