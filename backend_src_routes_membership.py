from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.membership import MembershipPlan, Subscription, Payment
from datetime import datetime, timedelta
import json

membership_bp = Blueprint('membership', __name__)

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

@membership_bp.route('/membership-plans', methods=['GET'])
def get_membership_plans():
    try:
        language = request.args.get('language', 'ar')
        
        plans = MembershipPlan.query.filter_by(is_active=True).all()
        plans_data = [plan.to_dict(language) for plan in plans]
        
        return jsonify({'plans': plans_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/membership-plans/<int:plan_id>', methods=['GET'])
def get_membership_plan(plan_id):
    try:
        language = request.args.get('language', 'ar')
        
        plan = MembershipPlan.query.get_or_404(plan_id)
        
        if not plan.is_active:
            return jsonify({'error': 'Plan not available'}), 404
        
        return jsonify({'plan': plan.to_dict(language)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        if not data.get('plan_id'):
            return jsonify({'error': 'plan_id is required'}), 400
        
        plan = MembershipPlan.query.get_or_404(data['plan_id'])
        
        if not plan.is_active:
            return jsonify({'error': 'Plan not available'}), 400
        
        # Check if user already has an active subscription
        existing_subscription = user.get_active_subscription()
        if existing_subscription:
            return jsonify({'error': 'You already have an active subscription'}), 400
        
        # Calculate subscription dates
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=plan.duration_days)
        
        # Create subscription
        subscription = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            start_date=start_date,
            end_date=end_date,
            status='pending',
            payment_status='pending',
            payment_method=data.get('payment_method', 'stripe')
        )
        
        db.session.add(subscription)
        db.session.flush()  # Get the subscription ID
        
        # Create payment record
        payment = Payment(
            user_id=user.id,
            amount=plan.price,
            currency=plan.currency,
            payment_method=data.get('payment_method', 'stripe'),
            payment_type='subscription',
            related_entity_type='subscription',
            related_entity_id=subscription.id,
            status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # TODO: Create payment intent with payment gateway
        # For now, we'll simulate successful payment
        
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': subscription.to_dict(),
            'payment': payment.to_dict(),
            'payment_intent': {
                'client_secret': f'pi_test_{payment.id}',
                'amount': plan.price,
                'currency': plan.currency
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/subscription/confirm-payment', methods=['POST'])
def confirm_subscription_payment():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        payment_id = data.get('payment_id')
        gateway_transaction_id = data.get('gateway_transaction_id')
        
        if not payment_id or not gateway_transaction_id:
            return jsonify({'error': 'Payment information required'}), 400
        
        # Find payment record
        payment = Payment.query.filter_by(
            id=payment_id,
            user_id=user.id,
            status='pending'
        ).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Update payment status
        payment.status = 'completed'
        payment.gateway_transaction_id = gateway_transaction_id
        payment.payment_date = datetime.utcnow()
        
        # Update subscription status
        subscription = Subscription.query.get(payment.related_entity_id)
        if subscription:
            subscription.status = 'active'
            subscription.payment_status = 'paid'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment confirmed successfully',
            'subscription': subscription.to_dict() if subscription else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/my-subscription', methods=['GET'])
def get_my_subscription():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        subscription = user.get_active_subscription()
        
        if not subscription:
            return jsonify({'subscription': None}), 200
        
        subscription_data = subscription.to_dict()
        subscription_data['plan'] = subscription.plan.to_dict()
        
        return jsonify({'subscription': subscription_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/subscription/cancel', methods=['POST'])
def cancel_subscription():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        subscription = user.get_active_subscription()
        
        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404
        
        # Cancel auto-renewal
        subscription.auto_renew = False
        subscription.status = 'cancelled'
        subscription.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription cancelled successfully',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/payment-methods', methods=['GET'])
def get_payment_methods():
    try:
        language = request.args.get('language', 'ar')
        
        payment_methods = {
            'ar': [
                {
                    'id': 'stripe',
                    'name': 'بطاقة ائتمان',
                    'description': 'فيزا، ماستركارد، أمريكان إكسبريس',
                    'icon': 'credit-card',
                    'supported_currencies': ['USD', 'EUR', 'EGP']
                },
                {
                    'id': 'paypal',
                    'name': 'PayPal',
                    'description': 'الدفع عبر PayPal',
                    'icon': 'paypal',
                    'supported_currencies': ['USD', 'EUR']
                },
                {
                    'id': 'fawry',
                    'name': 'فوري',
                    'description': 'الدفع عبر فوري',
                    'icon': 'mobile',
                    'supported_currencies': ['EGP']
                },
                {
                    'id': 'vodafone_cash',
                    'name': 'فودافون كاش',
                    'description': 'الدفع عبر فودافون كاش',
                    'icon': 'mobile',
                    'supported_currencies': ['EGP']
                }
            ],
            'en': [
                {
                    'id': 'stripe',
                    'name': 'Credit Card',
                    'description': 'Visa, Mastercard, American Express',
                    'icon': 'credit-card',
                    'supported_currencies': ['USD', 'EUR', 'EGP']
                },
                {
                    'id': 'paypal',
                    'name': 'PayPal',
                    'description': 'Pay with PayPal',
                    'icon': 'paypal',
                    'supported_currencies': ['USD', 'EUR']
                },
                {
                    'id': 'fawry',
                    'name': 'Fawry',
                    'description': 'Pay with Fawry',
                    'icon': 'mobile',
                    'supported_currencies': ['EGP']
                },
                {
                    'id': 'vodafone_cash',
                    'name': 'Vodafone Cash',
                    'description': 'Pay with Vodafone Cash',
                    'icon': 'mobile',
                    'supported_currencies': ['EGP']
                }
            ]
        }
        
        return jsonify({'payment_methods': payment_methods.get(language, payment_methods['en'])}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/my-payments', methods=['GET'])
def get_my_payments():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        payments = Payment.query.filter_by(user_id=user.id).order_by(Payment.payment_date.desc()).all()
        payments_data = [payment.to_dict() for payment in payments]
        
        return jsonify({'payments': payments_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin routes
@membership_bp.route('/admin/membership-plans', methods=['POST'])
def create_membership_plan():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        required_fields = ['name_ar', 'name_en', 'price', 'duration_days']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Prepare features JSON
        features = {}
        if data.get('features_ar'):
            features['ar'] = data['features_ar']
        if data.get('features_en'):
            features['en'] = data['features_en']
        
        plan = MembershipPlan(
            name_ar=data['name_ar'],
            name_en=data['name_en'],
            description_ar=data.get('description_ar', ''),
            description_en=data.get('description_en', ''),
            price=data['price'],
            currency=data.get('currency', 'EGP'),
            duration_days=data['duration_days'],
            plan_type=data.get('plan_type', 'monthly'),
            features=json.dumps(features) if features else None
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Membership plan created successfully',
            'plan': plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/admin/subscriptions', methods=['GET'])
def get_all_subscriptions():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        status_filter = request.args.get('status')
        plan_id = request.args.get('plan_id', type=int)
        
        query = Subscription.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if plan_id:
            query = query.filter_by(plan_id=plan_id)
        
        subscriptions = query.order_by(Subscription.created_at.desc()).all()
        
        subscriptions_data = []
        for subscription in subscriptions:
            subscription_dict = subscription.to_dict()
            subscription_dict['user'] = subscription.user.to_dict()
            subscription_dict['plan'] = subscription.plan.to_dict()
            subscriptions_data.append(subscription_dict)
        
        return jsonify({'subscriptions': subscriptions_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@membership_bp.route('/admin/payments', methods=['GET'])
def get_all_payments():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        status_filter = request.args.get('status')
        payment_method = request.args.get('payment_method')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Payment.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if payment_method:
            query = query.filter_by(payment_method=payment_method)
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Payment.payment_date >= date_from)
            except ValueError:
                return jsonify({'error': 'Invalid date_from format'}), 400
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(Payment.payment_date <= date_to)
            except ValueError:
                return jsonify({'error': 'Invalid date_to format'}), 400
        
        payments = query.order_by(Payment.payment_date.desc()).all()
        
        payments_data = []
        for payment in payments:
            payment_dict = payment.to_dict()
            payment_dict['user'] = payment.user.to_dict()
            payments_data.append(payment_dict)
        
        return jsonify({'payments': payments_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

