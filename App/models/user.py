from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, staff, employer

    def __init__(self, username, password, role='student'):
        self.username = username
        self.role = role
        self.set_password(password)

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_student(self):
        return self.role == 'student'
    
    def is_staff(self):
        return self.role == 'staff'
    
    def is_employer(self):
        return self.role == 'employer'
