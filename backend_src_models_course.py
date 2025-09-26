from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_ar = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(10), nullable=False, default='EGP')
    thumbnail_url = db.Column(db.String(500))
    duration_weeks = db.Column(db.Integer, default=4)
    level = db.Column(db.String(50), default='beginner')  # beginner, intermediate, advanced
    is_published = db.Column(db.Boolean, default=False)
    is_free = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('CourseModule', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy=True)
    
    def to_dict(self, language='ar'):
        return {
            'id': self.id,
            'title': self.title_ar if language == 'ar' else self.title_en,
            'description': self.description_ar if language == 'ar' else self.description_en,
            'price': self.price,
            'currency': self.currency,
            'thumbnail_url': self.thumbnail_url,
            'duration_weeks': self.duration_weeks,
            'level': self.level,
            'is_published': self.is_published,
            'is_free': self.is_free,
            'modules_count': len(self.modules),
            'students_count': len(self.enrollments),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CourseModule(db.Model):
    __tablename__ = 'course_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title_ar = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_ar = db.Column(db.Text)
    description_en = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('CourseLesson', backref='module', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, language='ar'):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title_ar if language == 'ar' else self.title_en,
            'description': self.description_ar if language == 'ar' else self.description_en,
            'order': self.order,
            'is_published': self.is_published,
            'lessons_count': len(self.lessons),
            'lessons': [lesson.to_dict(language) for lesson in sorted(self.lessons, key=lambda x: x.order)]
        }

class CourseLesson(db.Model):
    __tablename__ = 'course_lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'), nullable=False)
    title_ar = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    content_ar = db.Column(db.Text)
    content_en = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    pdf_url = db.Column(db.String(500))
    lesson_type = db.Column(db.String(50), default='video')  # video, text, pdf, quiz
    duration_minutes = db.Column(db.Integer, default=0)
    order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    is_free = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, language='ar'):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title_ar if language == 'ar' else self.title_en,
            'content': self.content_ar if language == 'ar' else self.content_en,
            'video_url': self.video_url,
            'pdf_url': self.pdf_url,
            'lesson_type': self.lesson_type,
            'duration_minutes': self.duration_minutes,
            'order': self.order,
            'is_published': self.is_published,
            'is_free': self.is_free
        }

class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    progress_percentage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='active')  # active, completed, cancelled
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    payment_id = db.Column(db.String(100))
    
    # Relationships
    progress = db.relationship('LessonProgress', backref='enrollment', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'progress_percentage': self.progress_percentage,
            'status': self.status,
            'payment_status': self.payment_status
        }

class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollments.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('course_lessons.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime)
    watch_time_seconds = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'enrollment_id': self.enrollment_id,
            'lesson_id': self.lesson_id,
            'is_completed': self.is_completed,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'watch_time_seconds': self.watch_time_seconds
        }

