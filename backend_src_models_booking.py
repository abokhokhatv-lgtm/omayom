from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_ar = db.Column(db.Text)
    description_en = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='EGP')
    duration_minutes = db.Column(db.Integer, default=60)
    service_type = db.Column(db.String(50), default='healing')  # healing, consultation, workshop, distance
    is_active = db.Column(db.Boolean, default=True)
    is_online = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='service', lazy=True)
    
    def to_dict(self, language='ar'):
        return {
            'id': self.id,
            'name': self.name_ar if language == 'ar' else self.name_en,
            'description': self.description_ar if language == 'ar' else self.description_en,
            'price': self.price,
            'currency': self.currency,
            'duration_minutes': self.duration_minutes,
            'service_type': self.service_type,
            'is_active': self.is_active,
            'is_online': self.is_online
        }

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='EGP')
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, completed, cancelled
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed, refunded
    payment_id = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))  # stripe, paypal, fawry, vodafone_cash
    meeting_link = db.Column(db.String(500))
    meeting_id = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'booking_time': self.booking_time.strftime('%H:%M') if self.booking_time else None,
            'duration_minutes': self.duration_minutes,
            'price': self.price,
            'currency': self.currency,
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'meeting_link': self.meeting_link,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AvailableSlot(db.Model):
    __tablename__ = 'available_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_pattern = db.Column(db.String(50))  # weekly, daily, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'is_available': self.is_available,
            'is_recurring': self.is_recurring,
            'recurring_pattern': self.recurring_pattern
        }

