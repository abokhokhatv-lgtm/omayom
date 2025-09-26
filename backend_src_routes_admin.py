from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.course import Course, CourseEnrollment
from src.models.booking import Booking, Service
from src.models.membership import Subscription, Payment, MembershipPlan
from src.models.marketing import NewsletterSubscriber, EmailCampaign, LandingPage, Coupon
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import json

admin_bp = Blueprint('admin', __name__)

def require_admin():
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return None, jsonify({'error': 'User not found'}), 404
    
    if user.role != 'admin':
        return None, jsonify({'error': 'Admin access required'}), 403
    
    return user, None, None

@admin_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Date range for statistics
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Users statistics
        total_users = User.query.count()
        new_users_this_month = User.query.filter(User.created_at >= start_date).count()
        active_subscribers = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.end_date > datetime.utcnow()
        ).count()
        
        # Revenue statistics
        total_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        
        monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date
        ).scalar() or 0
        
        # Bookings statistics
        total_bookings = Booking.query.count()
        pending_bookings = Booking.query.filter_by(status='pending').count()
        confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
        monthly_bookings = Booking.query.filter(Booking.created_at >= start_date).count()
        
        # Courses statistics
        total_courses = Course.query.count()
        published_courses = Course.query.filter_by(is_published=True).count()
        total_enrollments = CourseEnrollment.query.count()
        monthly_enrollments = CourseEnrollment.query.filter(
            CourseEnrollment.enrollment_date >= start_date
        ).count()
        
        # Newsletter statistics
        newsletter_subscribers = NewsletterSubscriber.query.filter_by(is_subscribed=True).count()
        monthly_newsletter_signups = NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed_at >= start_date
        ).count()
        
        # Top performing courses
        top_courses = db.session.query(
            Course.title_ar,
            Course.title_en,
            func.count(CourseEnrollment.id).label('enrollment_count')
        ).join(CourseEnrollment).group_by(Course.id).order_by(
            func.count(CourseEnrollment.id).desc()
        ).limit(5).all()
        
        # Recent activities
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
        recent_payments = Payment.query.filter_by(status='completed').order_by(
            Payment.payment_date.desc()
        ).limit(5).all()
        
        stats = {
            'overview': {
                'total_users': total_users,
                'new_users_this_month': new_users_this_month,
                'active_subscribers': active_subscribers,
                'total_revenue': total_revenue,
                'monthly_revenue': monthly_revenue,
                'total_bookings': total_bookings,
                'pending_bookings': pending_bookings,
                'confirmed_bookings': confirmed_bookings,
                'monthly_bookings': monthly_bookings,
                'total_courses': total_courses,
                'published_courses': published_courses,
                'total_enrollments': total_enrollments,
                'monthly_enrollments': monthly_enrollments,
                'newsletter_subscribers': newsletter_subscribers,
                'monthly_newsletter_signups': monthly_newsletter_signups
            },
            'top_courses': [
                {
                    'title_ar': course.title_ar,
                    'title_en': course.title_en,
                    'enrollment_count': course.enrollment_count
                }
                for course in top_courses
            ],
            'recent_activities': {
                'users': [user.to_dict() for user in recent_users],
                'bookings': [
                    {
                        **booking.to_dict(),
                        'user_name': booking.user.full_name,
                        'service_name': booking.service.name_ar
                    }
                    for booking in recent_bookings
                ],
                'payments': [
                    {
                        **payment.to_dict(),
                        'user_name': payment.user.full_name
                    }
                    for payment in recent_payments
                ]
            }
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/dashboard/revenue-chart', methods=['GET'])
def get_revenue_chart():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        period = request.args.get('period', 'month')  # month, quarter, year
        
        if period == 'month':
            # Last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            date_format = '%Y-%m-%d'
        elif period == 'quarter':
            # Last 3 months
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
            date_format = '%Y-%m'
        else:  # year
            # Last 12 months
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)
            date_format = '%Y-%m'
        
        # Get revenue data grouped by date
        revenue_data = db.session.query(
            func.date(Payment.payment_date).label('date'),
            func.sum(Payment.amount).label('revenue')
        ).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).group_by(func.date(Payment.payment_date)).all()
        
        # Format data for chart
        chart_data = []
        for data in revenue_data:
            chart_data.append({
                'date': data.date.strftime(date_format),
                'revenue': float(data.revenue)
            })
        
        return jsonify({'chart_data': chart_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/dashboard/users-chart', methods=['GET'])
def get_users_chart():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Last 30 days user registrations
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        users_data = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date,
            User.created_at <= end_date
        ).group_by(func.date(User.created_at)).all()
        
        chart_data = []
        for data in users_data:
            chart_data.append({
                'date': data.date.strftime('%Y-%m-%d'),
                'users': data.count
            })
        
        return jsonify({'chart_data': chart_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/dashboard/bookings-chart', methods=['GET'])
def get_bookings_chart():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Bookings by status
        bookings_by_status = db.session.query(
            Booking.status,
            func.count(Booking.id).label('count')
        ).group_by(Booking.status).all()
        
        # Bookings by service
        bookings_by_service = db.session.query(
            Service.name_ar,
            Service.name_en,
            func.count(Booking.id).label('count')
        ).join(Booking).group_by(Service.id).all()
        
        status_data = [
            {'status': booking.status, 'count': booking.count}
            for booking in bookings_by_status
        ]
        
        service_data = [
            {
                'service_ar': booking.name_ar,
                'service_en': booking.name_en,
                'count': booking.count
            }
            for booking in bookings_by_service
        ]
        
        return jsonify({
            'status_data': status_data,
            'service_data': service_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        role_filter = request.args.get('role')
        is_active = request.args.get('is_active')
        
        query = User.query
        
        if search:
            query = query.filter(
                or_(
                    User.username.contains(search),
                    User.email.contains(search),
                    User.first_name.contains(search),
                    User.last_name.contains(search)
                )
            )
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user_item in users.items:
            user_dict = user_item.to_dict()
            user_dict['has_active_subscription'] = user_item.has_active_subscription
            user_dict['total_bookings'] = Booking.query.filter_by(user_id=user_item.id).count()
            user_dict['total_payments'] = db.session.query(func.sum(Payment.amount)).filter_by(
                user_id=user_item.id, status='completed'
            ).scalar() or 0
            users_data.append(user_dict)
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        admin_user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'first_name', 'last_name', 'phone', 'role', 
            'is_active', 'is_verified'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reports/revenue', methods=['GET'])
def get_revenue_report():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        payment_method = request.args.get('payment_method')
        
        query = Payment.query.filter_by(status='completed')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Payment.payment_date >= start_date)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(Payment.payment_date <= end_date)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        if payment_method:
            query = query.filter_by(payment_method=payment_method)
        
        payments = query.order_by(Payment.payment_date.desc()).all()
        
        # Calculate totals
        total_amount = sum(payment.amount for payment in payments)
        payment_count = len(payments)
        
        # Group by payment method
        by_method = {}
        for payment in payments:
            method = payment.payment_method
            if method not in by_method:
                by_method[method] = {'count': 0, 'amount': 0}
            by_method[method]['count'] += 1
            by_method[method]['amount'] += payment.amount
        
        # Group by payment type
        by_type = {}
        for payment in payments:
            ptype = payment.payment_type
            if ptype not in by_type:
                by_type[ptype] = {'count': 0, 'amount': 0}
            by_type[ptype]['count'] += 1
            by_type[ptype]['amount'] += payment.amount
        
        payments_data = []
        for payment in payments:
            payment_dict = payment.to_dict()
            payment_dict['user_name'] = payment.user.full_name
            payments_data.append(payment_dict)
        
        return jsonify({
            'payments': payments_data,
            'summary': {
                'total_amount': total_amount,
                'payment_count': payment_count,
                'by_method': by_method,
                'by_type': by_type
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reports/courses', methods=['GET'])
def get_courses_report():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Course performance data
        courses_data = db.session.query(
            Course.id,
            Course.title_ar,
            Course.title_en,
            Course.price,
            Course.is_published,
            func.count(CourseEnrollment.id).label('enrollment_count'),
            func.avg(CourseEnrollment.progress_percentage).label('avg_progress')
        ).outerjoin(CourseEnrollment).group_by(Course.id).all()
        
        courses_report = []
        for course in courses_data:
            # Calculate revenue for this course
            course_revenue = db.session.query(func.sum(Payment.amount)).join(
                CourseEnrollment, Payment.related_entity_id == CourseEnrollment.id
            ).filter(
                CourseEnrollment.course_id == course.id,
                Payment.related_entity_type == 'course_enrollment',
                Payment.status == 'completed'
            ).scalar() or 0
            
            courses_report.append({
                'id': course.id,
                'title_ar': course.title_ar,
                'title_en': course.title_en,
                'price': course.price,
                'is_published': course.is_published,
                'enrollment_count': course.enrollment_count,
                'avg_progress': float(course.avg_progress) if course.avg_progress else 0,
                'revenue': float(course_revenue)
            })
        
        return jsonify({'courses': courses_report}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reports/marketing', methods=['GET'])
def get_marketing_report():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Newsletter statistics
        total_subscribers = NewsletterSubscriber.query.filter_by(is_subscribed=True).count()
        unsubscribed = NewsletterSubscriber.query.filter_by(is_subscribed=False).count()
        
        # Subscribers by language
        subscribers_by_language = db.session.query(
            NewsletterSubscriber.language_preference,
            func.count(NewsletterSubscriber.id).label('count')
        ).filter_by(is_subscribed=True).group_by(
            NewsletterSubscriber.language_preference
        ).all()
        
        # Email campaigns performance
        campaigns = EmailCampaign.query.all()
        campaigns_data = []
        for campaign in campaigns:
            campaigns_data.append({
                **campaign.to_dict(),
                'open_rate': (campaign.opened_count / campaign.recipients_count * 100) if campaign.recipients_count > 0 else 0,
                'click_rate': (campaign.clicked_count / campaign.recipients_count * 100) if campaign.recipients_count > 0 else 0
            })
        
        # Landing pages performance
        landing_pages = LandingPage.query.all()
        landing_pages_data = []
        for page in landing_pages:
            conversion_rate = (page.conversions_count / page.views_count * 100) if page.views_count > 0 else 0
            landing_pages_data.append({
                **page.to_dict(),
                'conversion_rate': conversion_rate
            })
        
        # Coupons usage
        coupons = Coupon.query.all()
        coupons_data = []
        for coupon in coupons:
            usage_rate = (coupon.used_count / coupon.usage_limit * 100) if coupon.usage_limit else 0
            coupons_data.append({
                **coupon.to_dict(),
                'usage_rate': usage_rate
            })
        
        return jsonify({
            'newsletter': {
                'total_subscribers': total_subscribers,
                'unsubscribed': unsubscribed,
                'by_language': [
                    {'language': sub.language_preference, 'count': sub.count}
                    for sub in subscribers_by_language
                ]
            },
            'campaigns': campaigns_data,
            'landing_pages': landing_pages_data,
            'coupons': coupons_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

