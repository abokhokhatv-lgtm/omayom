from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    language_preference = db.Column(db.String(10), default='ar')
    is_subscribed = db.Column(db.Boolean, default=True)
    subscription_source = db.Column(db.String(50))  # website, landing_page, manual
    tags = db.Column(db.Text)  # JSON string of tags
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    unsubscribed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        tags_list = []
        if self.tags:
            try:
                tags_list = json.loads(self.tags)
            except:
                pass
                
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'language_preference': self.language_preference,
            'is_subscribed': self.is_subscribed,
            'subscription_source': self.subscription_source,
            'tags': tags_list,
            'subscribed_at': self.subscribed_at.isoformat() if self.subscribed_at else None
        }

class EmailCampaign(db.Model):
    __tablename__ = 'email_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject_ar = db.Column(db.String(200))
    subject_en = db.Column(db.String(200))
    content_ar = db.Column(db.Text)
    content_en = db.Column(db.Text)
    campaign_type = db.Column(db.String(50), default='newsletter')  # newsletter, promotional, welcome, course
    target_audience = db.Column(db.String(50), default='all')  # all, subscribers, members, specific_tags
    target_tags = db.Column(db.Text)  # JSON string of target tags
    status = db.Column(db.String(50), default='draft')  # draft, scheduled, sent, cancelled
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    recipients_count = db.Column(db.Integer, default=0)
    opened_count = db.Column(db.Integer, default=0)
    clicked_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, language='ar'):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject_ar if language == 'ar' else self.subject_en,
            'content': self.content_ar if language == 'ar' else self.content_en,
            'campaign_type': self.campaign_type,
            'target_audience': self.target_audience,
            'status': self.status,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'recipients_count': self.recipients_count,
            'opened_count': self.opened_count,
            'clicked_count': self.clicked_count,
            'open_rate': (self.opened_count / self.recipients_count * 100) if self.recipients_count > 0 else 0,
            'click_rate': (self.clicked_count / self.recipients_count * 100) if self.recipients_count > 0 else 0
        }

class LandingPage(db.Model):
    __tablename__ = 'landing_pages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title_ar = db.Column(db.String(200))
    title_en = db.Column(db.String(200))
    description_ar = db.Column(db.Text)
    description_en = db.Column(db.Text)
    content_ar = db.Column(db.Text)
    content_en = db.Column(db.Text)
    cta_text_ar = db.Column(db.String(100))
    cta_text_en = db.Column(db.String(100))
    cta_link = db.Column(db.String(500))
    template = db.Column(db.String(50), default='default')
    is_published = db.Column(db.Boolean, default=False)
    seo_title_ar = db.Column(db.String(200))
    seo_title_en = db.Column(db.String(200))
    seo_description_ar = db.Column(db.Text)
    seo_description_en = db.Column(db.Text)
    views_count = db.Column(db.Integer, default=0)
    conversions_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, language='ar'):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'title': self.title_ar if language == 'ar' else self.title_en,
            'description': self.description_ar if language == 'ar' else self.description_en,
            'content': self.content_ar if language == 'ar' else self.content_en,
            'cta_text': self.cta_text_ar if language == 'ar' else self.cta_text_en,
            'cta_link': self.cta_link,
            'template': self.template,
            'is_published': self.is_published,
            'views_count': self.views_count,
            'conversions_count': self.conversions_count,
            'conversion_rate': (self.conversions_count / self.views_count * 100) if self.views_count > 0 else 0
        }

class Coupon(db.Model):
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name_ar = db.Column(db.String(200))
    name_en = db.Column(db.String(200))
    description_ar = db.Column(db.Text)
    description_en = db.Column(db.Text)
    discount_type = db.Column(db.String(20), default='percentage')  # percentage, fixed
    discount_value = db.Column(db.Float, nullable=False)
    minimum_amount = db.Column(db.Float, default=0)
    maximum_discount = db.Column(db.Float)
    usage_limit = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)
    applicable_to = db.Column(db.String(50), default='all')  # all, courses, bookings, subscriptions
    applicable_items = db.Column(db.Text)  # JSON string of specific item IDs
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, language='ar'):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name_ar if language == 'ar' else self.name_en,
            'description': self.description_ar if language == 'ar' else self.description_en,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'minimum_amount': self.minimum_amount,
            'maximum_discount': self.maximum_discount,
            'usage_limit': self.usage_limit,
            'used_count': self.used_count,
            'applicable_to': self.applicable_to,
            'is_active': self.is_active,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_valid': self.is_valid()
        }
    
    def is_valid(self):
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True

