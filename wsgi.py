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
    print('Database initialized')

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
    except Exception as e:
        print(f"❌ Error listing internships: {e}")

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

print("wsgi.py loaded successfully!")

# Application Commands 
application_cli = AppGroup('application', help='Application management commands')

@application_cli.command("create", help="Apply for an internship")
@click.argument("student_id", type=int)
@click.argument("internship_id", type=int)
def create_application_command(student_id, internship_id):
    from App.models import Application, User, Internship
    try:
        # Basic validation
        student = User.query.get(student_id)
        internship = Internship.query.get(internship_id)
        
        if not student:
            print(f"Student {student_id} not found")
            return
        if not internship:
            print(f"Internship {internship_id} not found")
            return
        
        application = Application(student_id=student_id, internship_id=internship_id)
        db.session.add(application)
        db.session.commit()
        print(f"Application created! Student {student_id} → Internship {internship_id}")
    except Exception as e:
        print(f"Error creating application: {e}")

@application_cli.command("list", help="List all applications")
def list_applications_command():
    from App.models import Application
    try:
        applications = Application.query.all()
        if not applications:
            print("No applications found.")
        else:
            for app in applications:
                print(f"{app.id}: Student {app.student_id} → Internship {app.internship_id} | Status: {app.status}")
    except Exception as e:
        print(f"Error listing applications: {e}")

app.cli.add_command(application_cli)

# Advanced Application Commands
@application_cli.command("shortlist", help="Shortlist an application (Staff only)")
@click.argument("application_id", type=int)
@click.argument("staff_id", type=int)
def shortlist_application_command(application_id, staff_id):
    from App.models import Application, User
    try:
        application = Application.query.get(application_id)
        staff = User.query.get(staff_id)
        
        if not application:
            print("Application not found")
            return
        if not staff or staff.role != 'staff':
            print("Only staff can shortlist applications")
            return
        
        application.status = 'shortlisted'
        db.session.commit()
        print(f"Application {application_id} shortlisted by Staff {staff_id}")
    except Exception as e:
        print(f"Error: {e}")

@application_cli.command("accept", help="Accept an application (Employer only)")
@click.argument("application_id", type=int)
@click.argument("employer_id", type=int)
def accept_application_command(application_id, employer_id):
    from App.models import Application, User, Internship
    try:
        application = Application.query.get(application_id)
        employer = User.query.get(employer_id)
        
        if not application:
            print("Application not found")
            return
        if not employer or employer.role != 'employer':
            print("Only employers can accept applications")
            return
        if application.internship.employer_id != employer_id:
            print("Employer can only accept applications for their own internships")
            return
        
        application.status = 'accepted'
        db.session.commit()
        print(f"Application {application_id} accepted by Employer {employer_id}")
    except Exception as e:
        print(f"Error: {e}")

@application_cli.command("reject", help="Reject an application (Employer only)")
@click.argument("application_id", type=int)
@click.argument("employer_id", type=int)
def reject_application_command(application_id, employer_id):
    from App.models import Application, User
    try:
        application = Application.query.get(application_id)
        employer = User.query.get(employer_id)
        
        if not application:
            print("Application not found")
            return
        if not employer or employer.role != 'employer':
            print("Only employers can reject applications")
            return
        if application.internship.employer_id != employer_id:
            print("Employer can only reject applications for their own internships")
            return
        
        application.status = 'rejected'
        db.session.commit()
        print(f"Application {application_id} rejected by Employer {employer_id}")
    except Exception as e:
        print(f"Error: {e}")

@application_cli.command("student", help="List applications for a specific student")
@click.argument("student_id", type=int)
def student_applications_command(student_id):
    from App.models import Application, User
    try:
        student = User.query.get(student_id)
        if not student:
            print("Student not found")
            return
        
        applications = Application.query.filter_by(student_id=student_id).all()
        if not applications:
            print(f"No applications found for student {student_id}")
        else:
            print(f"Applications for {student.username}:")
            for app in applications:
                print(f"  {app.id}: {app.internship.title} | Status: {app.status}")
    except Exception as e:
        print(f"Error: {e}")