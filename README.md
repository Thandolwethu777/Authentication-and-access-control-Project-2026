# Student Security Portal
### MariaDB Authentication and Access Control Project — 2026

**Course:** Database Systems  
**Institution:** Constructor University, Bremen  
**Project Type:** Group Project   
**Technologies:** MariaDB, Python, Flask, HTML, CSS, JavaScript,SQL



## 1. Project Overview

The Student Security Portal is a web-based application developed to demonstrate secure database authentication, authorization, and access control using MariaDB.

The application simulates a university academic management system in which students, teachers, and administrators interact with academic information according to their assigned permissions.

The main focus of the project is to demonstrate how database security mechanisms can protect sensitive information, prevent unauthorized operations, and enforce different access levels.

The system consists of three main components:

- **Frontend:** A user-friendly interface for logging in and accessing academic information.
- **Backend:** A Python Flask application that processes requests and communicates with MariaDB.
- **Database:** A MariaDB database that stores academic information and enforces the configured security policies.

## 2. Project Objectives

The primary objectives of this project are: #to be corrected 

1. Develop a functional web-based student management portal.
2. Implement secure database authentication.
3. Apply Role-Based Access Control (RBAC) to manage permissions.
4. Demonstrate MariaDB's `GRANT` and `DENY` mechanisms.
5. Configure a supported non-password database authentication method.
6. Protect database connections using TLS encryption and certificate verification.
7. Prevent unauthorized users from accessing or modifying restricted information.
8. Test the security implementation through authorized and unauthorized database operations.

## 3. Technologies Used 
##to be corrected

| Technology | Purpose |
|---|---|
| MariaDB | Relational database and access control |
| Python | Backend development |
| Flask | Web application framework |
| HTML | Webpage structure |
| CSS | User interface styling |
| JavaScript | Frontend functionality |
| Git and GitHub | Version control and collaboration |

## SET UP 

## Setup and Installation

Follow the instructions below to configure and run the Student Security Portal locally.

Prerequisites

Ensure the following software is installed:

MariaDB 13.1

Python 3

Git

A web browser

Step 1: Clone the Repository 

Clone the project from GitHub and navigate to the project directory.

## Frontend Development

### Technologies Used

The frontend was developed using the following technologies:

- **HTML5:** Defines the structure and content of the webpages.
- **CSS3:** Provides styling, layout, and visual consistency across the application.
- **JavaScript:** Handles user interactions, form submissions, and communication with the backend.

### Frontend Features

The frontend consists of the following main components:

**1. Login Page**

- Provides input fields for a username or email address and password.
- Includes a Sign In button to submit login credentials.
- Displays feedback messages when login attempts fail.
- Provides a consistent university-themed interface.

**2. Student Dashboard**

The student dashboard provides access to three main academic sections:

- **Grades:** Displays academic results available to the authenticated student.
- **Courses:** Displays course information.
- **Enrollment:** Displays the student's enrollment information.

**3. User Interface Design**

- Consistent layout and visual styling.
- Organized navigation between academic sections.
- Clearly labeled buttons, forms, and information panels.
- User-friendly presentation of academic information.

### Frontend Setup

Follow these instructions to view and run the frontend locally.

**Step 1: Clone the Repository**

```bash
git clone <repository-url>
cd Authentication-and-access-control-Project-2026
```

**Step 2: Open the Project**

Open the project folder in Visual Studio Code.

**Step 3: Start the Application**

The frontend is served through the Flask application. From the project directory, run:

```bash
py app.py
```

**Step 4: Open the Frontend**

Once the Flask development server is running, open the following address in a web browser:

http://127.0.0.1:5000

The Student Security Portal login page should appear.

**Note:** Running the complete application, including login and academic data retrieval, requires the backend and database to be configured. Refer to the backend and database setup sections for further instructions.

### Frontend Screenshots

**Login Page**
![Login Page](screenshots/loginpage.png)

**Student Dashboard**

[Insert screenshot of the student dashboard.]

**Grades, Courses, and Enrollment**

[Insert screenshots of the academic sections, if applicable.]

### Frontend and Backend Integration

The frontend communicates with the Flask backend using HTTP requests.

When a user submits the login form, JavaScript sends the entered credentials to the backend for verification. The frontend then processes the response and displays the appropriate result.

The frontend does not connect directly to MariaDB. Database operations, authentication, and access-control enforcement are handled by the backend and database components.

### Frontend Testing

The frontend was designed to support the following interactions:

| Feature | Expected Behavior |
|---|---|
| Login form | Accepts username/email and password |
| Sign In button | Submits a login request to the backend |
| Error messages | Displays feedback when login fails |
| Dashboard navigation | Allows users to navigate between sections |
| Grades section | Displays grade information returned by the backend |
| Courses section | Displays course information |
| Enrollment section | Displays enrollment information |

These interactions should be verified during final integration testing.

### Frontend Contribution// NOT SURE IF THIS IS COMPULSORY

The frontend development focused on designing and implementing the user interface of the Student Security Portal, including the login page, student dashboard, navigation components, styling, and integration with the backend API.

The objective was to provide an accessible and organized interface through which users could interact with the academic management system.


