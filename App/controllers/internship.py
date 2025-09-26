from App.models import Internship, User, UserRole, Application, ApplicationStatus
from App.database import db

def create_internship(title, description, employer_id):
    employer = User.query.get(employer_id)
    if not employer or not employer.is_employer():
        return None
    
    internship = Internship(
        title=title,
        description=description,
        employer_id=employer_id
    )
    db.session.add(internship)
    db.session.commit()
    return internship

def get_all_internships():
    return Internship.query.all()

def get_internship_by_id(internship_id):
    return Internship.query.get(internship_id)

def get_employer_internships(employer_id):
    return Internship.query.filter_by(employer_id=employer_id).all()