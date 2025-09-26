from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.course import Course, CourseModule, CourseLesson, CourseEnrollment, LessonProgress
from src.models.membership import Subscription
from datetime import datetime

courses_bp = Blueprint('courses', __name__)

def require_auth():
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return None, jsonify({'error': 'User not found'}), 404
    
    return user, None, None

def require_admin():
    user, error_response, status_code = require_auth()
    if error_response:
        return user, error_response, status_code
    
    if user.role != 'admin':
        return None, jsonify({'error': 'Admin access required'}), 403
    
    return user, None, None

@courses_bp.route('/courses', methods=['GET'])
def get_courses():
    try:
        language = request.args.get('language', 'ar')
        show_all = request.args.get('show_all', 'false').lower() == 'true'
        
        query = Course.query
        
        # If not admin, only show published courses
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        
        if not (user and user.role == 'admin') and not show_all:
            query = query.filter_by(is_published=True)
        
        courses = query.all()
        
        courses_data = []
        for course in courses:
            course_dict = course.to_dict(language)
            
            # Add enrollment status for authenticated users
            if user:
                enrollment = CourseEnrollment.query.filter_by(
                    user_id=user.id, 
                    course_id=course.id,
                    status='active'
                ).first()
                course_dict['is_enrolled'] = enrollment is not None
                course_dict['enrollment_progress'] = enrollment.progress_percentage if enrollment else 0
            else:
                course_dict['is_enrolled'] = False
                course_dict['enrollment_progress'] = 0
            
            courses_data.append(course_dict)
        
        return jsonify({'courses': courses_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    try:
        language = request.args.get('language', 'ar')
        
        course = Course.query.get_or_404(course_id)
        
        # Check if user can access this course
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        
        # If course is not published and user is not admin, deny access
        if not course.is_published and not (user and user.role == 'admin'):
            return jsonify({'error': 'Course not found'}), 404
        
        course_dict = course.to_dict(language)
        
        # Add modules with lessons
        modules_data = []
        for module in sorted(course.modules, key=lambda x: x.order):
            if module.is_published or (user and user.role == 'admin'):
                module_dict = module.to_dict(language)
                
                # Filter lessons based on access
                lessons_data = []
                for lesson in sorted(module.lessons, key=lambda x: x.order):
                    if lesson.is_published or (user and user.role == 'admin'):
                        lesson_dict = lesson.to_dict(language)
                        
                        # Check if user has access to this lesson
                        has_access = False
                        if lesson.is_free:
                            has_access = True
                        elif user:
                            # Check if user is enrolled or has active subscription
                            enrollment = CourseEnrollment.query.filter_by(
                                user_id=user.id, 
                                course_id=course.id,
                                status='active'
                            ).first()
                            has_access = enrollment is not None or user.has_active_subscription
                        
                        lesson_dict['has_access'] = has_access
                        
                        # Add progress for enrolled users
                        if user and has_access:
                            enrollment = CourseEnrollment.query.filter_by(
                                user_id=user.id, 
                                course_id=course.id
                            ).first()
                            if enrollment:
                                progress = LessonProgress.query.filter_by(
                                    enrollment_id=enrollment.id,
                                    lesson_id=lesson.id
                                ).first()
                                lesson_dict['is_completed'] = progress.is_completed if progress else False
                                lesson_dict['watch_time'] = progress.watch_time_seconds if progress else 0
                        
                        lessons_data.append(lesson_dict)
                
                module_dict['lessons'] = lessons_data
                modules_data.append(module_dict)
        
        course_dict['modules'] = modules_data
        
        # Add enrollment info for authenticated users
        if user:
            enrollment = CourseEnrollment.query.filter_by(
                user_id=user.id, 
                course_id=course.id,
                status='active'
            ).first()
            course_dict['is_enrolled'] = enrollment is not None
            course_dict['enrollment'] = enrollment.to_dict() if enrollment else None
        
        return jsonify({'course': course_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
def enroll_course(course_id):
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        course = Course.query.get_or_404(course_id)
        
        if not course.is_published:
            return jsonify({'error': 'Course not available'}), 400
        
        # Check if already enrolled
        existing_enrollment = CourseEnrollment.query.filter_by(
            user_id=user.id,
            course_id=course.id,
            status='active'
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Already enrolled in this course'}), 400
        
        # Check if course is free or user has active subscription
        if not course.is_free and not user.has_active_subscription:
            return jsonify({'error': 'Active subscription required'}), 403
        
        # Create enrollment
        enrollment = CourseEnrollment(
            user_id=user.id,
            course_id=course.id,
            status='active',
            payment_status='paid' if course.is_free else 'pending'
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': 'Enrolled successfully',
            'enrollment': enrollment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/courses/<int:course_id>/lessons/<int:lesson_id>/progress', methods=['POST'])
def update_lesson_progress(course_id, lesson_id):
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        # Get enrollment
        enrollment = CourseEnrollment.query.filter_by(
            user_id=user.id,
            course_id=course_id,
            status='active'
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        # Get or create lesson progress
        progress = LessonProgress.query.filter_by(
            enrollment_id=enrollment.id,
            lesson_id=lesson_id
        ).first()
        
        if not progress:
            progress = LessonProgress(
                enrollment_id=enrollment.id,
                lesson_id=lesson_id
            )
            db.session.add(progress)
        
        # Update progress
        if 'is_completed' in data:
            progress.is_completed = data['is_completed']
            if data['is_completed']:
                progress.completion_date = datetime.utcnow()
        
        if 'watch_time_seconds' in data:
            progress.watch_time_seconds = data['watch_time_seconds']
        
        db.session.commit()
        
        # Update overall course progress
        update_course_progress(enrollment.id)
        
        return jsonify({
            'message': 'Progress updated',
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def update_course_progress(enrollment_id):
    """Update overall course progress based on lesson completion"""
    try:
        enrollment = CourseEnrollment.query.get(enrollment_id)
        if not enrollment:
            return
        
        # Get all lessons in the course
        total_lessons = db.session.query(CourseLesson).join(CourseModule).filter(
            CourseModule.course_id == enrollment.course_id,
            CourseLesson.is_published == True
        ).count()
        
        if total_lessons == 0:
            return
        
        # Get completed lessons
        completed_lessons = db.session.query(LessonProgress).join(CourseLesson).join(CourseModule).filter(
            CourseModule.course_id == enrollment.course_id,
            LessonProgress.enrollment_id == enrollment_id,
            LessonProgress.is_completed == True
        ).count()
        
        # Calculate progress percentage
        progress_percentage = (completed_lessons / total_lessons) * 100
        enrollment.progress_percentage = progress_percentage
        
        # Mark as completed if 100%
        if progress_percentage >= 100:
            enrollment.status = 'completed'
            enrollment.completion_date = datetime.utcnow()
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()

@courses_bp.route('/my-courses', methods=['GET'])
def get_my_courses():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        language = request.args.get('language', 'ar')
        
        enrollments = CourseEnrollment.query.filter_by(user_id=user.id).all()
        
        courses_data = []
        for enrollment in enrollments:
            course_dict = enrollment.course.to_dict(language)
            course_dict['enrollment'] = enrollment.to_dict()
            courses_data.append(course_dict)
        
        return jsonify({'courses': courses_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin routes
@courses_bp.route('/admin/courses', methods=['POST'])
def create_course():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        required_fields = ['title_ar', 'title_en', 'description_ar', 'description_en']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        course = Course(
            title_ar=data['title_ar'],
            title_en=data['title_en'],
            description_ar=data['description_ar'],
            description_en=data['description_en'],
            price=data.get('price', 0),
            currency=data.get('currency', 'EGP'),
            duration_weeks=data.get('duration_weeks', 4),
            level=data.get('level', 'beginner'),
            is_free=data.get('is_free', False),
            thumbnail_url=data.get('thumbnail_url')
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Course created successfully',
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/admin/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        course = Course.query.get_or_404(course_id)
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'title_ar', 'title_en', 'description_ar', 'description_en',
            'price', 'currency', 'duration_weeks', 'level', 'is_published',
            'is_free', 'thumbnail_url'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(course, field, data[field])
        
        course.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Course updated successfully',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

