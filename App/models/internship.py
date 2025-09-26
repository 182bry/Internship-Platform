from App.database import db
from datetime import datetime

class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    employer = db.relationship("User", backref="internships", foreign_keys=[employer_id])

    def __repr__(self):
        return f'<Internship {self.title} by Employer {self.employer_id}>'
    
    def get_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'employer_id': self.employer_id,
            'employer_username': self.employer.username if self.employer else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
