import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.main import create_app
from App.database import db, get_migrate

app = create_app()
migrate = get_migrate(app)

# Init Command
@app.cli.command("init", help="Creates and initializes the database")
def init():
    db.drop_all()
    db.create_all()
    # Pre-populate users
    from App.controllers.user import create_student, create_staff, create_employer
    create_student('student1', 'pass')
    create_staff('staff1', 'pass')
    create_employer('employer1', 'pass')
    print('Database initialized with default users')

# User Commands 
user_cli = AppGroup('user', help='User object commands')

@user_cli.command("create", help="Creates a user")
@click.argument("username")
@click.argument("password")
@click.argument("role", required=False)  # Make role optional
def create_user_command(username, password, role=None):
    from App.models import User
    try:
        # Set default role if not provided
        if role is None:
            role = "student"
            
        # Validate role
        valid_roles = ['student', 'staff', 'employer']
        if role not in valid_roles:
            print(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
            return
            
        user = User(username=username, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        print(f'User {username} ({role}) created!')
    except Exception as e:
        print(f'Error creating user: {e}')

@user_cli.command("list", help="Lists users in the database")
def list_user_command():
    from App.models import User
    users = User.query.all()
    for user in users:
        print(f'{user.id}: {user.username} ({user.role})')

app.cli.add_command(user_cli)

# Internship Commands 
internship_cli = AppGroup('internship', help='Internship object commands')

@internship_cli.command("create", help="Create an internship position")
@click.argument("employer_id", type=int)
@click.argument("title")
@click.argument("description")
def create_internship_command(employer_id, title, description):
    from App.models import Internship, User
    try:
        # Basic validation - check if user exists
        employer = User.query.get(employer_id)
        if not employer:
            print(f"User {employer_id} not found")
            return
        
        internship = Internship(title=title, description=description, employer_id=employer_id)
        db.session.add(internship)
        db.session.commit()
        print(f"Internship '{title}' created successfully!")
    except Exception as e:
        print(f"Error creating internship: {e}")

@internship_cli.command("list", help="List all internships")
def list_internships_command():
    from App.models import Internship
    try:
        internships = Internship.query.all()
        if not internships:
            print("No internships found.")
        else:
            for internship in internships:
                print(f"{internship.id}: {internship.title} - Employer: {internship.employer_id}")
                if internship.description:
                    print(f"   Description: {internship.description}")

    except Exception as e:
        print(f"Error listing internships: {e}")

app.cli.add_command(internship_cli)

# Test Commands
test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    
app.cli.add_command(test)

#print("wsgi.py loaded successfully!")

# Application Commands
from App.controllers.application import (
    create_application,
    shortlist_application,
    accept_application,
    reject_application,
    get_student_applications
)

# Create the CLI group
application_cli = AppGroup('application', help='Application management commands')

# Student applies
@application_cli.command("create", help="Apply for an internship")
@click.argument("student_id", type=int)
@click.argument("internship_id", type=int)
def create_application_command(student_id, internship_id):
    app_obj = create_application(student_id, internship_id)
    if app_obj is None:
        print("Cannot create application. Make sure the user is a student and the internship exists.")
    else:
        print(f"Application created! Student {student_id} → Internship {internship_id}")

# Staff shortlists
@application_cli.command("shortlist", help="Shortlist an application (Staff only)")
@click.argument("application_id", type=int)
@click.argument("staff_id", type=int)
def shortlist_application_command(application_id, staff_id):
    app_obj = shortlist_application(application_id, staff_id)
    if app_obj is None:
        print("Cannot shortlist application. Only staff can shortlist valid applications.")
    else:
        print(f"Application {application_id} shortlisted by Staff {staff_id}")

# Employer accepts
@application_cli.command("accept", help="Accept an application (Employer only)")
@click.argument("application_id", type=int)
@click.argument("employer_id", type=int)
def accept_application_command(application_id, employer_id):
    app_obj = accept_application(application_id, employer_id)
    if app_obj is None:
        print("Cannot accept application. Only the employer who owns the internship can accept.")
    else:
        print(f"Application {application_id} accepted by Employer {employer_id}")

# Employer rejects
@application_cli.command("reject", help="Reject an application (Employer only)")
@click.argument("application_id", type=int)
@click.argument("employer_id", type=int)
def reject_application_command(application_id, employer_id):
    app_obj = reject_application(application_id, employer_id)
    if app_obj is None:
        print("Cannot reject application. Only the employer who owns the internship can reject.")
    else:
        print(f"Application {application_id} rejected by Employer {employer_id}")

# List all applications
@application_cli.command("list", help="List all applications")
def list_applications_command():
    from App.models.application import Application  # Import the model here
    applications = Application.query.all()
    if not applications:
        print("No applications found.")
    else:
        for app_obj in applications:
            student_name = app_obj.student.username if app_obj.student else f"Student {app_obj.student_id}"
            internship_title = app_obj.internship.title if app_obj.internship else f"Internship {app_obj.internship_id}"
            print(f"{app_obj.id}: {student_name} → {internship_title} | Status: {app_obj.status}")

# Student views their applications
@application_cli.command("student", help="List applications for a specific student")
@click.argument("student_id", type=int)
def student_applications_command(student_id):
    applications = get_student_applications(student_id)
    if not applications:
        print(f"No applications found for student {student_id}")
    else:
        print(f"Applications for student {student_id}:")
        for app_obj in applications:
            internship_title = app_obj.internship.title if app_obj.internship else "Unknown"
            student_name = app_obj.student.username if app_obj.student else f"Student {app_obj.student_id}"
            print(f"  {app_obj.id}: {internship_title} | {student_name} | Status: {app_obj.status}")

# Register the CLI group with the Flask app
app.cli.add_command(application_cli)
