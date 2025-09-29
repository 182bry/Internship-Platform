from App.models import Application, User, Internship
from App.database import db

def create_application(student_id, internship_id):
    student = User.query.get(student_id)
    internship = Internship.query.get(internship_id)
    
    if not student or not student.is_student() or not internship:
        return None
    
    application = Application(
        student_id=student_id,
        internship_id=internship_id,
        status='pending'  
    )
    db.session.add(application)
    db.session.commit()
    return application

def shortlist_application(application_id, staff_id):
    application = Application.query.get(application_id)
    staff = User.query.get(staff_id)
    
    if not application or not staff or not staff.is_staff():
        return None
    
    application.status = 'shortlisted'
    db.session.commit()
    return application

def accept_application(application_id, employer_id):
    application = Application.query.get(application_id)
    employer = User.query.get(employer_id)
    
    if (not application or not employer or not employer.is_employer() or 
        application.internship.employer_id != employer_id):
        return None
    
    application.status = 'accepted'
    db.session.commit()
    return application

def reject_application(application_id, employer_id):
    application = Application.query.get(application_id)
    employer = User.query.get(employer_id)
    
    if (not application or not employer or not employer.is_employer() or 
        application.internship.employer_id != employer_id):
        return None
    
    application.status = 'rejected'
    db.session.commit()
    return application

def get_student_applications(student_id):
    return Application.query.filter_by(student_id=student_id).all()
