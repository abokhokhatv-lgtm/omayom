from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.course import Course, CourseModule, CourseLesson
from src.models.booking import Service, AvailableSlot
from src.models.membership import MembershipPlan
from src.models.marketing import NewsletterSubscriber, LandingPage, Coupon
from datetime import datetime, time, timedelta
import json
from werkzeug.security import generate_password_hash

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/initialize', methods=['POST'])
def initialize_system():
    """Initialize the system with default data"""
    try:
        # Check if system is already initialized
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            return jsonify({'message': 'System already initialized'}), 200

        # Create admin user
        admin_password = 'OmarAli2025!'
        admin_user = User(
            username='omarali_admin',
            email='abokhokhatv@gmail.com',
            password_hash=generate_password_hash(admin_password),
            first_name='Omar',
            last_name='Ali',
            role='admin',
            is_active=True,
            is_verified=True,
            language_preference='ar'
        )
        db.session.add(admin_user)
        db.session.flush()

        # Create membership plans
        monthly_plan = MembershipPlan(
            name_ar='اشتراك شهري',
            name_en='Monthly Membership',
            description_ar='وصول كامل لجميع الكورسات والمحتوى الحصري',
            description_en='Full access to all courses and exclusive content',
            price=12.0,
            currency='USD',
            duration_days=30,
            plan_type='monthly',
            features=json.dumps({
                'ar': [
                    'وصول لجميع الكورسات',
                    'محتوى جديد أسبوعياً',
                    'جلسات مباشرة شهرية',
                    'مجتمع الأعضاء الخاص',
                    'شهادات إتمام',
                    'دعم فني 24/7'
                ],
                'en': [
                    'Access to all courses',
                    'New content weekly',
                    'Monthly live sessions',
                    'Private member community',
                    'Completion certificates',
                    '24/7 technical support'
                ]
            })
        )
        
        yearly_plan = MembershipPlan(
            name_ar='اشتراك سنوي',
            name_en='Yearly Membership',
            description_ar='وصول كامل لجميع الكورسات مع خصم 20%',
            description_en='Full access to all courses with 20% discount',
            price=115.0,  # 20% discount from 144
            currency='USD',
            duration_days=365,
            plan_type='yearly',
            features=json.dumps({
                'ar': [
                    'وصول لجميع الكورسات',
                    'محتوى جديد أسبوعياً',
                    'جلسات مباشرة شهرية',
                    'مجتمع الأعضاء الخاص',
                    'شهادات إتمام',
                    'دعم فني 24/7',
                    'خصم 20%',
                    'استشارة شخصية مجانية'
                ],
                'en': [
                    'Access to all courses',
                    'New content weekly',
                    'Monthly live sessions',
                    'Private member community',
                    'Completion certificates',
                    '24/7 technical support',
                    '20% discount',
                    'Free personal consultation'
                ]
            })
        )
        
        db.session.add(monthly_plan)
        db.session.add(yearly_plan)
        db.session.flush()

        # Create services
        services = [
            {
                'name_ar': 'جلسة الشفاء الروحاني',
                'name_en': 'Spiritual Healing Session',
                'description_ar': 'جلسة فردية مخصصة لتطهير الطاقة السلبية وتحقيق التوازن الداخلي',
                'description_en': 'Individual session dedicated to cleansing negative energy and achieving inner balance',
                'price': 25.0,
                'duration_minutes': 60,
                'service_type': 'healing',
                'is_online': True
            },
            {
                'name_ar': 'الاستشارة الروحانية',
                'name_en': 'Spiritual Consultation',
                'description_ar': 'جلسة إرشاد روحاني لمساعدتك في اتخاذ القرارات المهمة',
                'description_en': 'Spiritual guidance session to help you make important decisions',
                'price': 20.0,
                'duration_minutes': 45,
                'service_type': 'consultation',
                'is_online': True
            },
            {
                'name_ar': 'ورشة تدريبية جماعية',
                'name_en': 'Group Training Workshop',
                'description_ar': 'ورشة جماعية لتعلم تقنيات الشفاء الذاتي والتأمل العميق',
                'description_en': 'Group workshop to learn self-healing techniques and deep meditation',
                'price': 40.0,
                'duration_minutes': 180,
                'service_type': 'workshop',
                'is_online': False
            },
            {
                'name_ar': 'الشفاء عن بُعد',
                'name_en': 'Distance Healing',
                'description_ar': 'جلسة شفاء روحاني عبر الإنترنت للأشخاص غير القادرين على الحضور شخصياً',
                'description_en': 'Online spiritual healing session for people who cannot attend in person',
                'price': 22.0,
                'duration_minutes': 45,
                'service_type': 'distance_healing',
                'is_online': True
            }
        ]

        for service_data in services:
            service = Service(**service_data)
            db.session.add(service)

        # Create default available slots (Saturday, Monday, Wednesday 6-9 PM Cairo time)
        weekdays = [5, 0, 2]  # Saturday=5, Monday=0, Wednesday=2
        times = [
            (time(18, 0), time(19, 0)),   # 6-7 PM
            (time(19, 0), time(20, 0)),   # 7-8 PM
            (time(20, 0), time(21, 0)),   # 8-9 PM
        ]

        start_date = datetime.now().date()
        for i in range(30):  # Next 30 days
            current_date = start_date + timedelta(days=i)
            if current_date.weekday() in weekdays:
                for start_time, end_time in times:
                    slot = AvailableSlot(
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        is_recurring=True,
                        recurring_pattern='weekly'
                    )
                    db.session.add(slot)

        # Create free course
        free_course = Course(
            title_ar='مقدمة في الشفاء الروحاني',
            title_en='Introduction to Spiritual Healing',
            description_ar='ابدأ رحلتك في عالم الشفاء الروحاني مع هذا الكورس المجاني',
            description_en='Start your journey in the world of spiritual healing with this free course',
            price=0.0,
            currency='USD',
            level='beginner',
            duration_weeks=1,
            is_published=True,
            is_free=True,
            instructor_id=admin_user.id
        )
        db.session.add(free_course)
        db.session.flush()

        # Create modules for free course
        free_modules = [
            {
                'title_ar': 'أساسيات الطاقة الروحانية',
                'title_en': 'Basics of Spiritual Energy',
                'description_ar': 'تعرف على مفهوم الطاقة الروحانية وأهميتها',
                'description_en': 'Learn about the concept of spiritual energy and its importance',
                'order_index': 1
            },
            {
                'title_ar': 'تقنيات التأمل الأساسية',
                'title_en': 'Basic Meditation Techniques',
                'description_ar': 'تعلم تقنيات التأمل البسيطة والفعالة',
                'description_en': 'Learn simple and effective meditation techniques',
                'order_index': 2
            },
            {
                'title_ar': 'تطهير الطاقة السلبية',
                'title_en': 'Cleansing Negative Energy',
                'description_ar': 'طرق التخلص من الطاقة السلبية المتراكمة',
                'description_en': 'Methods to eliminate accumulated negative energy',
                'order_index': 3
            },
            {
                'title_ar': 'تحقيق التوازن الداخلي',
                'title_en': 'Achieving Inner Balance',
                'description_ar': 'كيفية الوصول للتوازن والسلام الداخلي',
                'description_en': 'How to achieve balance and inner peace',
                'order_index': 4
            }
        ]

        for module_data in free_modules:
            module = CourseModule(
                course_id=free_course.id,
                **module_data
            )
            db.session.add(module)
            db.session.flush()

            # Add lessons to each module
            lesson = Lesson(
                module_id=module.id,
                title_ar=f'درس {module_data["title_ar"]}',
                title_en=f'Lesson {module_data["title_en"]}',
                content_ar=f'محتوى الدرس حول {module_data["title_ar"]}. هذا محتوى تجريبي يمكن تعديله من لوحة التحكم.',
                content_en=f'Lesson content about {module_data["title_en"]}. This is sample content that can be edited from the admin panel.',
                lesson_type='text',
                duration_minutes=15,
                order_index=1,
                is_published=True
            )
            db.session.add(lesson)

        # Create paid course
        paid_course = Course(
            title_ar='الريكي - المستوى الأول',
            title_en='Reiki - Level One',
            description_ar='تعلم أساسيات تقنية الريكي للشفاء الذاتي ومساعدة الآخرين',
            description_en='Learn the fundamentals of Reiki technique for self-healing and helping others',
            price=49.0,
            currency='USD',
            level='beginner',
            duration_weeks=4,
            is_published=True,
            is_free=False,
            instructor_id=admin_user.id
        )
        db.session.add(paid_course)
        db.session.flush()

        # Create TikTok landing page
        tiktok_page = LandingPage(
            name='TikTok Landing Page',
            slug='tiktok',
            title_ar='مرحباً بك من TikTok!',
            title_en='Welcome from TikTok!',
            description_ar='اكتشف قوة الشفاء الروحاني مع عمر علي',
            description_en='Discover the Power of Spiritual Healing with Omar Ali',
            content_ar='صفحة هبوط خاصة لمتابعي TikTok',
            content_en='Special landing page for TikTok followers',
            cta_text_ar='ابدأ رحلتك الروحانية',
            cta_text_en='Start Your Spiritual Journey',
            cta_link='/courses',
            template='tiktok',
            is_published=True,
            seo_title_ar='عمر علي - المعالج الروحاني | TikTok',
            seo_title_en='Omar Ali - Spiritual Healer | TikTok',
            seo_description_ar='اكتشف قوة الشفاء الروحاني مع المعالج عمر علي. كورسات مجانية وجلسات شفاء',
            seo_description_en='Discover the power of spiritual healing with healer Omar Ali. Free courses and healing sessions'
        )
        db.session.add(tiktok_page)

        # Create TikTok coupon
        tiktok_coupon = Coupon(
            code='TIKTOK20',
            name_ar='خصم TikTok',
            name_en='TikTok Discount',
            description_ar='خصم 20% لمتابعي TikTok',
            description_en='20% discount for TikTok followers',
            discount_type='percentage',
            discount_value=20.0,
            minimum_amount=10.0,
            usage_limit=100,
            applicable_to='all',
            valid_from=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(tiktok_coupon)

        # Commit all changes
        db.session.commit()

        return jsonify({
            'message': 'System initialized successfully',
            'admin_credentials': {
                'email': 'abokhokhatv@gmail.com',
                'password': admin_password,
                'username': 'omarali_admin'
            },
            'features_created': {
                'admin_user': True,
                'membership_plans': 2,
                'services': 4,
                'available_slots': 'Next 30 days',
                'free_course': True,
                'paid_course': True,
                'tiktok_landing': True,
                'tiktok_coupon': True
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@setup_bp.route('/status', methods=['GET'])
def get_setup_status():
    """Check if system is initialized"""
    try:
        admin_user = User.query.filter_by(role='admin').first()
        courses_count = Course.query.count()
        services_count = Service.query.count()
        plans_count = MembershipPlan.query.count()
        
        return jsonify({
            'initialized': admin_user is not None,
            'admin_exists': admin_user is not None,
            'courses_count': courses_count,
            'services_count': services_count,
            'membership_plans_count': plans_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

