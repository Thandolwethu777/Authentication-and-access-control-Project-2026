# Student Security Portal
### MariaDB Authentication and Access Control Project — 2026

**Constructor University, Bremen | Databases | Topic 5: Authentication and Access Control**

## 1. Project Overview

We built a small university portal to demonstrate authentication and access control in MariaDB 13.1. The database stores students, lecturers, courses, enrolments, grades and application accounts. Students can view their own academic information, lecturers can view their assigned courses and enrolled students, and administrators can manage academic records, including grades.

Our aim was to see how roles, GRANT, DENY, PARSEC and TLS work in practice, and to test which unauthorized operations they prevent. We also use password hashing and session-based authorization in the web application.

The system has three parts: the frontend sends HTTP requests to Flask, Flask checks the user's session and permissions and communicates with MariaDB, and MariaDB returns the results. Flask sends JSON back to the frontend. The browser never connects directly to MariaDB.

## 2. Requirements

These instructions are for Windows with a fresh installation of MariaDB 13.1 on port `3306`.

- MariaDB Server 13.1 (database development and TLS testing used 13.1.1).
- Python 3.13.
- Git, a web browser and a text editor such as VS Code.
- HeidiSQL or another MariaDB client (the command-line client is sufficient).

The Python dependencies are Flask, MariaDB Connector/Python, python-dotenv and Werkzeug.

## 3. Getting Started

Open PowerShell and clone the repository:

```powershell
git clone https://github.com/Thandolwethu777/Authentication-and-access-control-Project-2026.git
cd Authentication-and-access-control-Project-2026
```

Create a virtual environment and install the required Python dependencies by running the following commands in PowerShell:



```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install Flask mariadb python-dotenv Werkzeug
```
## 4. MariaDB

We used HeidiSQL to create and test our database. The schema and sample records are stored separately so the database can be recreated easily.

### 4.1 Database schema

The table below shows what each table stores. It is a logical overview, rather than a complete list of SQL types and constraints.

| Table | Primary key | Other main fields | Relationships / purpose |
|---|---|---|---|
| `students` | `student_id` | `student_number`, `first_name`, `last_name`, `email` | Student details |
| `lecturers` | `lecturer_id` | `first_name`, `last_name`, `email`, `department` | Lecturer details |
| `courses` | `course_id` | `course_code`, `course_name` | Course details; assigned lecturer in the integrated application |
| `enrolments` | `enrolment_id` | `student_id`, `course_id`, `enrolment_date` | Links students to courses |
| `grades` | `grade_id` | `enrolment_id`, `grade` | Links grades to enrolments |
| `app_users` | `user_id` | `username`, `email`, `app_role`, `student_id`, `lecturer_id`, `password_hash`, `is_active`, `created_at` | Portal login and account identity |


### 4.2 Create the database and insert sample data

Open HeidiSQL and connect to the MariaDB server as root using host `127.0.0.1` and port `3306`.

Open and execute the following SQL files from the repository in this order:

1. `schema.sql` — creates the database and its tables.
2. `sample_data.sql` — populates the tables with sample records.

Run the following SQL commands to verify that the database has been created and populated successfully:

```sql
USE constructor_security;
SHOW TABLES;
SELECT * FROM students;
SELECT * FROM courses;
```

The sample data includes student numbers CU001–CU003 and course codes CS101, CS201 and EC101. Use these identifiers when looking up student and course IDs.

### 4.3 Roles, GRANT and DENY

Run the role and user creation scripts as an administrator. The main database roles are `student_role`, `lecturer_role` and `admin_role`. The application connects using a separate account, `backend_user`, with `backend_role` as its default role.

The setup uses `roles.sql`, `deny.sql` and `deny_tests.sql`. Open each script first and execute `roles.sql` followed by `deny.sql` as administrator, after schema and sample data. In HeidiSQL, open each SQL file and execute its contents. 

Verify the permissions assigned to each role by running:

```sql
SHOW GRANTS FOR student_role;
SHOW GRANTS FOR lecturer_role;
SHOW GRANTS FOR admin_role;
SHOW GRANTS FOR backend_role;
SHOW GRANTS FOR portal_demo_role;
```

Roles group permissions so that they do not have to be assigned to each user individually. DENY allows an explicit exception to a broader grant. The separate demonstration in Section 7.1 shows how this works.

## 5. Backend

The backend was built with Python, Flask, MariaDB Connector/Python, python-dotenv and Werkzeug. `db.py` handles the connection settings. `backend_user` authenticates through PARSEC, using `backend_role` as its default role. The role has SELECT permissions needed by the application and INSERT/UPDATE access for grades, but cannot delete grade records. The backend setup also includes password validation, password reuse prevention and a UNIQUE constraint on `grades.enrolment_id`.

The login endpoint retrieves the user from `app_users` and verifies the password hash. After successful login, Flask stores the user ID, username and application role in the session. Protected routes check authentication and role before processing requests; unauthorized requests receive status codes such as 401 or 403. Logout clears the session.

| Access | Method and endpoint | Purpose |
|---|---|---|
| Authentication | POST `/login`, POST `/logout` | Sign in and sign out |
| Authenticated user | GET `/account-info` | Account information |
| Student | GET `/my-courses`, `/my-grades`, `/my-enrolments`, `/my-lecturers` | Own academic information |
| Lecturer | GET `/lecturer/students`, `/my-courses` | Assigned courses and enrolled students |
| Administrator | GET `/students`, `/lecturers`, `/admin/courses`, `/admin/enrolments`, `/admin/grades` | Administrative records |
| Administrator | PATCH `/admin/grades/<grade_id>` | Update a grade after validation |

These application roles are distinct from MariaDB database roles: all website requests use the backend database account, while Flask applies user-specific access restrictions.

### 5.1 PARSEC and database password policies

In the administrator SQL session, check the server version,
plugin directory and PARSEC status:

```sql
SELECT VERSION();
SHOW VARIABLES LIKE 'plugin_dir';

SELECT PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_LIBRARY
FROM information_schema.PLUGINS
WHERE PLUGIN_NAME LIKE '%parsec%';
```

If PARSEC is already ACTIVE, no additional installation
is required. A NULL value under PLUGIN_LIBRARY indicates
that the plugin is built into the server.

In our MariaDB 13.1.1 Windows installation, PARSEC is
built into the server.

If PARSEC is not listed and the server-side shared
library is available, execute:

```sql
INSTALL SONAME 'auth_parsec';
```

Verify that PARSEC is ACTIVE before proceeding.
The client-side parsec.dll must not be installed
as a server plugin.

Create the dedicated account (only if it does not
already exist), replacing the placeholder with a strong
private password. The backend role must already exist
from `roles.sql`.

```sql
CREATE USER 'backend_user'@'localhost'
IDENTIFIED VIA parsec USING PASSWORD('ReplaceWithYourOwnStrongPassword!');

GRANT backend_role TO 'backend_user'@'localhost';

SET DEFAULT ROLE backend_role FOR 'backend_user'@'localhost';

SHOW GRANTS FOR 'backend_user'@'localhost';
SHOW GRANTS FOR backend_role;
```

Connect as `backend_user` in a separate PowerShell terminal:

```powershell
& "C:\Program Files\MariaDB 13.1\bin\mariadb.exe" --no-defaults --protocol=tcp --host=127.0.0.1 --port=3306 --user=backend_user --plugin-dir="C:\Program Files\MariaDB 13.1\lib\plugin" -p
```

Adjust the installation path and port if necessary.
Enter the password chosen when creating `backend_user`.

Verify the authenticated account and active role:

```sql
SELECT CURRENT_USER(), CURRENT_ROLE();
SELECT * FROM constructor_security.courses;
```

The account should authenticate and `backend_role`
should be active. Test grade deletion as described in
Section 7.2. PARSEC authenticates the database connection;
it does not replace the portal user's password hash
or eliminate the local database secret.

#### Password complexity and reuse prevention

Return to the administrator SQL session. Install each
plugin only if it is not already active:

```sql
INSTALL SONAME 'simple_password_check';

SET GLOBAL simple_password_check_minimal_length = 8;
SET GLOBAL simple_password_check_digits = 1;
SET GLOBAL simple_password_check_letters_same_case = 1;
SET GLOBAL simple_password_check_other_characters = 1;

SHOW VARIABLES LIKE 'simple_password_check%';

INSTALL SONAME 'password_reuse_check';

SET GLOBAL password_reuse_check_interval = 0;

SHOW VARIABLES LIKE 'password_reuse_check_interval';
SHOW PLUGINS;
```

Check both plugins are active. The password policy requires eight characters, uppercase and lowercase letters, a digit and a non-alphanumeric character. An interval of zero retains password history indefinitely. Runtime settings may not persist after restart; if persistent configuration is needed, back up the server configuration, add the corresponding options, restart and verify them. Test using disposable accounts, not the application's working credentials (Section 7.2).

### 5.2 Create portal login accounts

These accounts are stored in `app_users`, separate from MariaDB server accounts. Generate a Werkzeug hash separately for each chosen portal password:

```powershell
.\.venv\Scripts\python.exe -c "from werkzeug.security import generate_password_hash; print(generate_password_hash(input('Enter portal password to hash: ')))"
```

Keep the plaintext passwords privately for login testing. Copy only the complete generated hash into the SQL statements. As database administrator, inspect the actual schema and sample records:

```sql
USE constructor_security;
DESCRIBE app_users;
SELECT * FROM students;
SELECT * FROM lecturers;
```

Use the student and lecturer IDs returned by the queries above. Replace each hash placeholder with the corresponding generated hash. Choose unique usernames and email addresses.

```sql
INSERT INTO app_users
 (username, email, app_role, student_id, lecturer_id, password_hash, is_active)
VALUES ('student.login', 'student@example.test', 'student', 1, NULL,
 'PASTE_STUDENT_HASH_HERE', TRUE);

INSERT INTO app_users
 (username, email, app_role, student_id, lecturer_id, password_hash, is_active)
VALUES ('lecturer.login', 'lecturer@example.test', 'lecturer', NULL, 1,
 'PASTE_LECTURER_HASH_HERE', TRUE);

INSERT INTO app_users
 (username, email, app_role, student_id, lecturer_id, password_hash, is_active)
VALUES ('admin.login', 'admin@example.test', 'admin', NULL, NULL,
 'PASTE_ADMIN_HASH_HERE', TRUE);

SELECT user_id, username, email, app_role, student_id, lecturer_id, is_active
FROM app_users;
```

The IDs of 1 are examples only. Verify account links and active status.

### 5.3 Configure Flask and TLS

Create a local `.env` file in the project root:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=backend_user
DB_PASSWORD=your_local_database_password
DB_NAME=constructor_security
DB_PLUGIN_DIR=C:\Program Files\MariaDB 13.1\lib\plugin
FLASK_SECRET_KEY=your_generated_flask_secret_key
```

Replace the password and plugin directory with the actual local values. Generate a private Flask secret key with:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into `.env`. Do not commit `.env`, real passwords or secret keys. Keep `.env` out of Git using `.gitignore`.

The `db.py` connection uses `ssl=True` and `ssl_verify_cert=True` in `mariadb.connect()` to request encryption and certificate verification. Do not disable certificate verification to resolve connection errors.

Run the TLS verification script from the project root:

```powershell
.\.venv\Scripts\python.exe test_tls.py
```

The script should show a nonempty TLS version and cipher. Our results are shown in Section 7.3.

## 6. Frontend

The frontend was developed with HTML5, CSS3 and JavaScript. It includes a university-themed login page, feedback for unsuccessful logins and dashboard navigation. Students can view grades, courses and enrolments. JavaScript sends requests to Flask and displays the returned information. The frontend does not handle database connections or serve as the final security boundary.

**Login page**

![Login page](screenshots/loginpage.png)

⭐ Student dashboard

⭐ Grades, courses and enrolments

### 6.1 Run the application

Make sure MariaDB is running. From the project folder, run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 in a browser. Sign in with `student.login`, `lecturer.login` or `admin.login` and the password you chose for that account. Flask serves the frontend, so no separate web server is needed.

## 7. Security Testing

Below are our findings and the tests used to check the security controls. Expected outcomes are listed separately from observed results.

### 7.1 Database roles and DENY

Connect using the student, lecturer and administrator database test accounts and verify their assigned roles with `SELECT CURRENT_USER(), CURRENT_ROLE();`. Test an allowed and a prohibited operation for each role.

The separate DENY test uses the following policy:

```sql
CREATE ROLE IF NOT EXISTS portal_demo_role;
GRANT SELECT ON constructor_security.* TO portal_demo_role;
DENY SELECT ON constructor_security.app_users TO portal_demo_role;
CREATE USER IF NOT EXISTS 'deny_test'@'localhost' IDENTIFIED BY 'ReplaceWithTestPassword!';
GRANT portal_demo_role TO 'deny_test'@'localhost';
SET DEFAULT ROLE portal_demo_role FOR 'deny_test'@'localhost';
```

Replace the example password with a private test password. If the script already created this account, use the password configured there.

As administrator, run `SHOW GRANTS FOR portal_demo_role;`. Open a new HeidiSQL session as `deny_test` and execute the statements in `deny_tests.sql` one at a time:

```sql
SELECT CURRENT_USER(), CURRENT_ROLE();
SELECT * FROM constructor_security.courses;
SELECT * FROM constructor_security.app_users;
```

The courses query succeeded, while the app_users query was rejected. This demonstrated that an explicit DENY can override a broader GRANT. A failed login alone is not evidence of DENY: the account must first authenticate successfully.

**Evidence:**

⭐ DENY role grants

⭐ Allowed courses query

⭐ Blocked app_users query

For the student and lecturer DENY policy, repeat direct database tests as student and lecturer accounts, checking that students cannot read `app_users` or update/delete grades and lecturers cannot delete grades. Use safe no-row update/delete probes or disposable data. Record actual outcomes separately from the `portal_demo_role` demonstration.

### 7.2 PARSEC, database permissions and password policies

These are the expected results for the backend security tests.

| Control | How to retest | Expected outcome |
|---|---|---|
| PARSEC | Connect as backend_user with correct credentials, then with incorrect credentials | Valid login succeeds; invalid login is rejected |
| Default role | Check `CURRENT_ROLE()` as backend_user | backend_role |
| Grade deletion restriction | Attempt to delete an existing disposable grade as backend_user on the test database | Permission error |
| Password validation | Attempt to set a weak password on a disposable database account | Rejected |
| Password reuse prevention | Attempt to reuse a previously used password on a disposable account | Rejected according to policy |
| UNIQUE constraint | Attempt a second grade insert for an enrolment that already has a grade | Duplicate-key error |

The database password policy requires at least eight characters, an uppercase letter, a lowercase letter, a digit and a special character. These database policies do not automatically apply to website passwords stored in `app_users`.

Use disposable records and accounts for destructive tests; do not run them against data you need to retain. For password validation and reuse, the following test sequence is a way to reproduce the test (choose private, distinct test passwords meeting the policy):

```sql
-- Administrator session; weak password should be rejected.
CREATE USER 'policy_test'@'localhost' IDENTIFIED BY 'weak';
-- If rejected, create the account with a strong password instead.
CREATE USER 'policy_test'@'localhost' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD_A';
ALTER USER 'policy_test'@'localhost' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD_B';
-- Reuse of password A should be rejected.
ALTER USER 'policy_test'@'localhost' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD_A';
```

If the weak creation unexpectedly succeeds, stop and investigate rather than continuing with the same account name. Save the actual outcomes without showing secrets. For the DELETE restriction, connect as backend_user and attempt `DELETE FROM constructor_security.grades WHERE 1=0;` (a safe permission probe); record whether permission is denied. 


### 7.3 TLS encryption, enforcement and verification

First connect using the MariaDB command-line client. Use port 3306.

```powershell
$dbPort = 3306
$client = 'C:\Program Files\MariaDB 13.1\bin\mariadb.exe'
& $client --host=127.0.0.1 --port=$dbPort --user=root --ssl -p
```

Run these SQL statements:

```sql
SHOW GLOBAL VARIABLES WHERE Variable_name IN ('have_ssl', 'tls_version', 'require_secure_transport');
SHOW SESSION STATUS WHERE Variable_name IN ('Ssl_version', 'Ssl_cipher');
```

Our server reported TLS support and our session returned:

```text
Ssl_version = TLSv1.3
Ssl_cipher  = TLS_AES_256_GCM_SHA384
```

The exact cipher may vary with the server and client. We also found that `require_secure_transport` was OFF and an account without a TLS requirement could connect without encryption. TLS support alone was therefore not enough to guarantee encrypted connections.

Create a dedicated disposable TLS test account as an administrator, replacing the password placeholder locally with a password that meets the configured policy:

```sql
CREATE USER 'tls_test_user'@'127.0.0.1'
IDENTIFIED BY 'REPLACE_WITH_UNIQUE_TEST_PASSWORD' REQUIRE SSL;
```

Exit the SQL client and attempt a connection without TLS:

```powershell
& $client --host=127.0.0.1 --port=$dbPort --user=tls_test_user --skip-ssl -p
```

This connection was rejected in our test. Use the same account and password to connect with TLS:

```powershell
& $client --host=127.0.0.1 --port=$dbPort --user=tls_test_user --ssl --ssl-verify-server-cert -p
```

The encrypted connection succeeded. In the SQL client, run `STATUS;` and the session-status query above. Our client reported `cert is OK` and the negotiated TLS cipher. If authentication fails in both cases, check the account host and password before interpreting the result as TLS enforcement.

Finally, run `test_tls.py` using the configured Flask environment, as shown in Section 5. Our results were:

```text
TLS cipher: [('Ssl_cipher', 'TLS_AES_256_GCM_SHA384')]
TLS version: [('Ssl_version', 'TLSv1.3')]
```



### 7.4 Website authentication, authorization and frontend tests

Use the following tests to check the complete portal:

| Test | Expected outcome |
|---|---|
| Valid credentials for each demo role | Login succeeds and appropriate information is displayed |
| Incorrect password | Login rejected and error feedback displayed |
| Missing login fields | Request rejected |
| Inactive account | Login rejected |
| Invalid grade update | Rejected |
| Student attempts admin grade update | Forbidden |
| Student dashboard navigation | Own grades, courses and enrolments displayed |
| Lecturer access | Only assigned courses and their enrolled students displayed |
| Student or lecturer requests GET `/students` or `/admin/grades` directly while logged in | 403 or other appropriate denial; no restricted data returned |
| Administrator grade update with valid input on disposable data | Authorized update succeeds |
| Logged-out request to protected endpoint | 401 or other appropriate denial |
| Logout | Session cleared; protected requests denied |

For direct GET tests, open the endpoint on the same host and port in the browser while logged in as the relevant user. Check the actual HTTP status in browser developer tools. Test access to another student's records as well as administrator-only routes; hiding buttons is not sufficient evidence of authorization.

## 8. Findings

We found that roles made permissions easier to manage. Our DENY test showed that a user with broad read access could still be prevented from reading account information.

Another important finding was that TLS support does not mean every connection is encrypted. We were initially able to connect without TLS, but the connection was rejected when we used an account with REQUIRE SSL. Our Python connection reported TLS 1.3 and a nonempty cipher.

Authentication and authorization are different. A successful login identifies a user, but permissions and backend checks determine what that user can do. PARSEC protects database authentication, while Werkzeug hashes protect portal passwords.

## 9. Limitations

TLS enforcement was demonstrated on a dedicated test account rather than globally. Although the client accepted the server certificate, we did not independently test rejection of untrusted certificates or hostname mismatches.

Flask uses a shared database account, so individual portal users depend on the backend's role checks and row filtering. The database password policies do not automatically apply to portal passwords. The separate DENY demonstration does not by itself prove row-level isolation.

The application is an educational project running on a local Flask development server, not a production deployment.

## 10. Conclusion

Through this project we learned how database permissions, authentication and encrypted connections work together. We divided the work into MariaDB, backend and frontend development and combined the components into one university portal. Testing both allowed and forbidden operations helped us understand what each security control actually protects.
