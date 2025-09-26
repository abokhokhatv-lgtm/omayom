from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class MembershipPlan(db.Model):
    __tablename__ = 'membership_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_ar = db.Column(db.Text)
    description_en = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='EGP')
    duration_days = db.Column(db.Integer, default=30)  # 30 for monthly, 365 for yearly
    plan_type = db.Column(db.String(50), default='monthly')  # monthly, yearly
    features = db.Column(db.Text)  # JSON string of features
    is_active = db.Column(db.Boolean, default=True)
    stripe_price_id = db.Column(db.String(100))
    paypal_plan_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='plan', lazy=True)
    
    def to_dict(self, language='ar'):
        features_list = []
        if self.features:
            try:
                features_data = json.loads(self.features)
                features_list = features_data.get(language, [])
            except:
                pass
                
        return {
            'id': self.id,
            'name': self.name_ar if language == 'ar' else self.name_en,
            'description': self.description_ar if language == 'ar' else self.description_en,
            'price': self.price,
            'currency': self.currency,
            'duration_days': self.duration_days,
            'plan_type': self.plan_type,
            'features': features_list,
            'is_active': self.is_active
        }

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('membership_plans.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='active')  # active, cancelled, expired, pending
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    payment_method = db.Column(db.String(50))  # stripe, paypal, fawry, vodafone_cash
    payment_id = db.Column(db.String(100))
    stripe_subscription_id = db.Column(db.String(100))
    auto_renew = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'auto_renew': self.auto_renew,
            'days_remaining': (self.end_date - datetime.utcnow()).days if self.end_date else 0
        }
    
    @property
    def is_active(self):
        return self.status == 'active' and self.end_date > datetime.utcnow()

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='EGP')
    payment_method = db.Column(db.String(50), nullable=False)  # stripe, paypal, fawry, vodafone_cash
    payment_gateway = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    gateway_transaction_id = db.Column(db.String(100))
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed, cancelled, refunded
    payment_type = db.Column(db.String(50))  # subscription, booking, course
    related_entity_type = db.Column(db.String(50))  # subscription, booking, course_enrollment
    related_entity_id = db.Column(db.Integer)
    payment_metadata = db.Column(db.Text)  # JSON string for additional data
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        metadata_dict = {}
        if self.payment_metadata:
            try:
                metadata_dict = json.loads(self.payment_metadata)
            except:
                pass
                
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'payment_gateway': self.payment_gateway,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'payment_type': self.payment_type,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'metadata': metadata_dict,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None
        }

