from App.database import db

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, shortlisted, accepted, rejected
    
    # Relationships
    student = db.relationship('User', backref=db.backref('applications', lazy=True))
    internship = db.relationship('Internship', backref=db.backref('applications', lazy=True))
    
    def __init__(self, student_id, internship_id, status='pending'):
        self.student_id = student_id
        self.internship_id = internship_id
        self.status = status
    
    def get_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'internship_id': self.internship_id,
            'status': self.status,
            'student_name': self.student.username if self.student else None,
            'internship_title': self.internship.title if self.internship else None
        }
