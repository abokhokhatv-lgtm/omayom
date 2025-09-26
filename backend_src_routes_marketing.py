from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.marketing import NewsletterSubscriber, EmailCampaign, LandingPage, Coupon
from datetime import datetime
import json
import re

marketing_bp = Blueprint('marketing', __name__)

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

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@marketing_bp.route('/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if already subscribed
        existing_subscriber = NewsletterSubscriber.query.filter_by(email=email).first()
        
        if existing_subscriber:
            if existing_subscriber.is_subscribed:
                return jsonify({'message': 'Already subscribed to newsletter'}), 200
            else:
                # Reactivate subscription
                existing_subscriber.is_subscribed = True
                existing_subscriber.unsubscribed_at = None
                existing_subscriber.subscribed_at = datetime.utcnow()
        else:
            # Create new subscriber
            subscriber = NewsletterSubscriber(
                email=email,
                name=data.get('name', '').strip(),
                language_preference=data.get('language_preference', 'ar'),
                subscription_source=data.get('source', 'website')
            )
            db.session.add(subscriber)
        
        db.session.commit()
        
        # TODO: Send welcome email
        
        return jsonify({'message': 'Successfully subscribed to newsletter'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/newsletter/unsubscribe', methods=['POST'])
def unsubscribe_newsletter():
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        subscriber = NewsletterSubscriber.query.filter_by(email=email).first()
        
        if not subscriber:
            return jsonify({'error': 'Email not found in newsletter'}), 404
        
        subscriber.is_subscribed = False
        subscriber.unsubscribed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Successfully unsubscribed from newsletter'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/landing-pages/<slug>', methods=['GET'])
def get_landing_page(slug):
    try:
        language = request.args.get('language', 'ar')
        
        landing_page = LandingPage.query.filter_by(slug=slug, is_published=True).first()
        
        if not landing_page:
            return jsonify({'error': 'Landing page not found'}), 404
        
        # Increment views count
        landing_page.views_count += 1
        db.session.commit()
        
        return jsonify({'landing_page': landing_page.to_dict(language)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/landing-pages/<slug>/convert', methods=['POST'])
def track_conversion(slug):
    try:
        landing_page = LandingPage.query.filter_by(slug=slug, is_published=True).first()
        
        if not landing_page:
            return jsonify({'error': 'Landing page not found'}), 404
        
        # Increment conversions count
        landing_page.conversions_count += 1
        db.session.commit()
        
        return jsonify({'message': 'Conversion tracked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/coupons/validate', methods=['POST'])
def validate_coupon():
    try:
        data = request.get_json()
        
        if not data.get('code'):
            return jsonify({'error': 'Coupon code is required'}), 400
        
        code = data['code'].strip().upper()
        applicable_to = data.get('applicable_to', 'all')
        amount = data.get('amount', 0)
        
        coupon = Coupon.query.filter_by(code=code).first()
        
        if not coupon:
            return jsonify({'error': 'Invalid coupon code'}), 404
        
        if not coupon.is_valid():
            return jsonify({'error': 'Coupon is expired or not active'}), 400
        
        # Check if coupon is applicable
        if coupon.applicable_to != 'all' and coupon.applicable_to != applicable_to:
            return jsonify({'error': 'Coupon not applicable to this item'}), 400
        
        # Check minimum amount
        if amount < coupon.minimum_amount:
            return jsonify({'error': f'Minimum amount required: {coupon.minimum_amount}'}), 400
        
        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount_amount = (amount * coupon.discount_value) / 100
            if coupon.maximum_discount:
                discount_amount = min(discount_amount, coupon.maximum_discount)
        else:  # fixed
            discount_amount = coupon.discount_value
        
        final_amount = max(0, amount - discount_amount)
        
        return jsonify({
            'valid': True,
            'coupon': coupon.to_dict(),
            'discount_amount': discount_amount,
            'final_amount': final_amount
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/coupons/apply', methods=['POST'])
def apply_coupon():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        if not data.get('code'):
            return jsonify({'error': 'Coupon code is required'}), 400
        
        code = data['code'].strip().upper()
        
        coupon = Coupon.query.filter_by(code=code).first()
        
        if not coupon or not coupon.is_valid():
            return jsonify({'error': 'Invalid or expired coupon'}), 400
        
        # Increment usage count
        coupon.used_count += 1
        db.session.commit()
        
        return jsonify({
            'message': 'Coupon applied successfully',
            'coupon': coupon.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin routes
@marketing_bp.route('/admin/newsletter/subscribers', methods=['GET'])
def get_newsletter_subscribers():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        is_subscribed = request.args.get('is_subscribed')
        language = request.args.get('language')
        source = request.args.get('source')
        
        query = NewsletterSubscriber.query
        
        if is_subscribed is not None:
            query = query.filter_by(is_subscribed=is_subscribed.lower() == 'true')
        
        if language:
            query = query.filter_by(language_preference=language)
        
        if source:
            query = query.filter_by(subscription_source=source)
        
        subscribers = query.order_by(NewsletterSubscriber.subscribed_at.desc()).all()
        subscribers_data = [subscriber.to_dict() for subscriber in subscribers]
        
        return jsonify({'subscribers': subscribers_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/admin/email-campaigns', methods=['POST'])
def create_email_campaign():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        required_fields = ['name', 'subject_ar', 'subject_en', 'content_ar', 'content_en']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        campaign = EmailCampaign(
            name=data['name'],
            subject_ar=data['subject_ar'],
            subject_en=data['subject_en'],
            content_ar=data['content_ar'],
            content_en=data['content_en'],
            campaign_type=data.get('campaign_type', 'newsletter'),
            target_audience=data.get('target_audience', 'all'),
            target_tags=json.dumps(data.get('target_tags', [])) if data.get('target_tags') else None
        )
        
        if data.get('scheduled_at'):
            try:
                campaign.scheduled_at = datetime.strptime(data['scheduled_at'], '%Y-%m-%d %H:%M:%S')
                campaign.status = 'scheduled'
            except ValueError:
                return jsonify({'error': 'Invalid scheduled_at format. Use YYYY-MM-DD HH:MM:SS'}), 400
        
        db.session.add(campaign)
        db.session.commit()
        
        return jsonify({
            'message': 'Email campaign created successfully',
            'campaign': campaign.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/admin/email-campaigns', methods=['GET'])
def get_email_campaigns():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        language = request.args.get('language', 'ar')
        status_filter = request.args.get('status')
        campaign_type = request.args.get('campaign_type')
        
        query = EmailCampaign.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if campaign_type:
            query = query.filter_by(campaign_type=campaign_type)
        
        campaigns = query.order_by(EmailCampaign.created_at.desc()).all()
        campaigns_data = [campaign.to_dict(language) for campaign in campaigns]
        
        return jsonify({'campaigns': campaigns_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/admin/landing-pages', methods=['POST'])
def create_landing_page():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        required_fields = ['name', 'slug', 'title_ar', 'title_en']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if slug already exists
        existing_page = LandingPage.query.filter_by(slug=data['slug']).first()
        if existing_page:
            return jsonify({'error': 'Slug already exists'}), 400
        
        landing_page = LandingPage(
            name=data['name'],
            slug=data['slug'],
            title_ar=data['title_ar'],
            title_en=data['title_en'],
            description_ar=data.get('description_ar', ''),
            description_en=data.get('description_en', ''),
            content_ar=data.get('content_ar', ''),
            content_en=data.get('content_en', ''),
            cta_text_ar=data.get('cta_text_ar', ''),
            cta_text_en=data.get('cta_text_en', ''),
            cta_link=data.get('cta_link', ''),
            template=data.get('template', 'default'),
            seo_title_ar=data.get('seo_title_ar', ''),
            seo_title_en=data.get('seo_title_en', ''),
            seo_description_ar=data.get('seo_description_ar', ''),
            seo_description_en=data.get('seo_description_en', '')
        )
        
        db.session.add(landing_page)
        db.session.commit()
        
        return jsonify({
            'message': 'Landing page created successfully',
            'landing_page': landing_page.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/admin/coupons', methods=['POST'])
def create_coupon():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        required_fields = ['code', 'discount_type', 'discount_value']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        code = data['code'].strip().upper()
        
        # Check if code already exists
        existing_coupon = Coupon.query.filter_by(code=code).first()
        if existing_coupon:
            return jsonify({'error': 'Coupon code already exists'}), 400
        
        coupon = Coupon(
            code=code,
            name_ar=data.get('name_ar', ''),
            name_en=data.get('name_en', ''),
            description_ar=data.get('description_ar', ''),
            description_en=data.get('description_en', ''),
            discount_type=data['discount_type'],
            discount_value=data['discount_value'],
            minimum_amount=data.get('minimum_amount', 0),
            maximum_discount=data.get('maximum_discount'),
            usage_limit=data.get('usage_limit'),
            applicable_to=data.get('applicable_to', 'all'),
            applicable_items=json.dumps(data.get('applicable_items', [])) if data.get('applicable_items') else None
        )
        
        if data.get('valid_from'):
            try:
                coupon.valid_from = datetime.strptime(data['valid_from'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return jsonify({'error': 'Invalid valid_from format. Use YYYY-MM-DD HH:MM:SS'}), 400
        
        if data.get('valid_until'):
            try:
                coupon.valid_until = datetime.strptime(data['valid_until'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return jsonify({'error': 'Invalid valid_until format. Use YYYY-MM-DD HH:MM:SS'}), 400
        
        db.session.add(coupon)
        db.session.commit()
        
        return jsonify({
            'message': 'Coupon created successfully',
            'coupon': coupon.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/admin/coupons', methods=['GET'])
def get_coupons():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        language = request.args.get('language', 'ar')
        is_active = request.args.get('is_active')
        applicable_to = request.args.get('applicable_to')
        
        query = Coupon.query
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        if applicable_to:
            query = query.filter_by(applicable_to=applicable_to)
        
        coupons = query.order_by(Coupon.created_at.desc()).all()
        coupons_data = [coupon.to_dict(language) for coupon in coupons]
        
        return jsonify({'coupons': coupons_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

