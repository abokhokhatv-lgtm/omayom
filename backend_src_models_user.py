from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    language_preference = db.Column(db.String(10), default='ar')
    timezone = db.Column(db.String(50), default='Africa/Cairo')
    profile_picture = db.Column(db.String(500))
    bio = db.Column(db.Text)
    role = db.Column(db.String(20), default='user')  # user, admin, moderator
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    enrollments = db.relationship('CourseEnrollment', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'language_preference': self.language_preference,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'gender': self.gender,
                'timezone': self.timezone,
                'email_verified_at': self.email_verified_at.isoformat() if self.email_verified_at else None
            })
            
        return data
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def has_active_subscription(self):
        from src.models.membership import Subscription
        active_sub = Subscription.query.filter_by(
            user_id=self.id, 
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).first()
        return active_sub is not None
    
    def get_active_subscription(self):
        from src.models.membership import Subscription
        return Subscription.query.filter_by(
            user_id=self.id, 
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).first()
