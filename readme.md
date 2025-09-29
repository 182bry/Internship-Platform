# Internship Platform CLI

A **Flask-based command-line application** for managing internship applications, shortlisting, and employer responses.  
Built using the **MVC architecture pattern** with role-based user access.

---

## Features

- **Employer**
  - Create internship positions  
  - Accept/reject students from shortlist  

- **Staff**
  - Shortlist students for internship positions  

- **Student**
  - View shortlisted positions and employer responses  

---

## Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/182bry/Internship-Platform.git
cd InternshipPlatform
```

3. **Optional- Open project in VS Code
code . # opens the current folder in a new VS Code window, ensuring all files and subfolders are visible

4. **Create virtual environment**
```bash
python -m venv venv
```
# Windows
```bash
venv\Scripts\activate
```
# Linux/Mac
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

6. **Initialize Database**
```bash
flask init
```
# CLI Commands Reference
User Management:
```bash
# Create users with roles (student, staff, employer)
flask user create <username> <password> <role>

# List all users
flask user list
``` 
Internship Management:
```bash
# Create internship position (Employer only)
flask internship create <employer_id> "<title>" "<description>"

# List all internships
flask internship list
```
Application Workflow:
```bash
# Apply for internship (Student only)
flask application create <student_id> <internship_id>

# Shortlist application (Staff only)
flask application shortlist <application_id> <staff_id>

# Accept/Reject application (Employer only)
flask application accept <application_id> <employer_id>
flask application reject <application_id> <employer_id>

# View all applications
flask application list

# View student's applications
flask application student <student_id>
```

**Example Workflow:**
Setup Users:
flask user create alice alicepass student
flask user create bob bobpass staff
flask user create charlie charliepass employer

Create Internship:
flask internship create 3 "Software Developer" "Build web applications"

Student Applies:
flask application create 1 1

Staff Shortlists:
flask application shortlist 1 2

Employer Decides:
flask application accept 1 3

Student Views Status:
flask application student 1

**Database Migrations:**
If models change, update the database schema:
```bash
flask db init
flask db migrate
flask db upgrade
```

**Notes**
- The database comes pre-populated with default users for easier testing (student1, staff1, employer1).

- Make sure to activate the virtual environment before running CLI commands.

- Role-based restrictions are enforced in the CLI: only valid users can perform certain actions.

