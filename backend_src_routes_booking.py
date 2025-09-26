from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.booking import Service, Booking, AvailableSlot
from datetime import datetime, date, time, timedelta
import json

booking_bp = Blueprint('booking', __name__)

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

@booking_bp.route('/services', methods=['GET'])
def get_services():
    try:
        language = request.args.get('language', 'ar')
        
        services = Service.query.filter_by(is_active=True).all()
        services_data = [service.to_dict(language) for service in services]
        
        return jsonify({'services': services_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    try:
        language = request.args.get('language', 'ar')
        
        service = Service.query.get_or_404(service_id)
        
        if not service.is_active:
            return jsonify({'error': 'Service not available'}), 404
        
        return jsonify({'service': service.to_dict(language)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/available-slots', methods=['GET'])
def get_available_slots():
    try:
        service_id = request.args.get('service_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not service_id:
            return jsonify({'error': 'service_id is required'}), 400
        
        service = Service.query.get_or_404(service_id)
        
        # Parse dates
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start_date = date.today()
            
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                end_date = start_date + timedelta(days=14)  # Default 2 weeks
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get available slots
        available_slots = AvailableSlot.query.filter(
            AvailableSlot.date >= start_date,
            AvailableSlot.date <= end_date,
            AvailableSlot.is_available == True
        ).all()
        
        # Get existing bookings to exclude booked slots
        existing_bookings = Booking.query.filter(
            Booking.service_id == service_id,
            Booking.booking_date >= start_date,
            Booking.booking_date <= end_date,
            Booking.status.in_(['pending', 'confirmed'])
        ).all()
        
        # Create a set of booked slots for quick lookup
        booked_slots = set()
        for booking in existing_bookings:
            slot_key = f"{booking.booking_date}_{booking.booking_time}"
            booked_slots.add(slot_key)
        
        # Filter available slots
        available_times = []
        for slot in available_slots:
            slot_key = f"{slot.date}_{slot.start_time}"
            if slot_key not in booked_slots:
                available_times.append({
                    'date': slot.date.isoformat(),
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'duration_minutes': service.duration_minutes
                })
        
        # If no predefined slots, generate default slots
        if not available_times:
            available_times = generate_default_slots(start_date, end_date, service, booked_slots)
        
        return jsonify({'available_slots': available_times}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_default_slots(start_date, end_date, service, booked_slots):
    """Generate default available slots if none are predefined"""
    default_times = [
        time(9, 0), time(10, 30), time(12, 0), 
        time(13, 30), time(15, 0), time(16, 30), time(18, 0)
    ]
    
    available_times = []
    current_date = start_date
    
    while current_date <= end_date:
        # Skip weekends for default slots
        if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
            for slot_time in default_times:
                slot_key = f"{current_date}_{slot_time}"
                if slot_key not in booked_slots:
                    end_time = (datetime.combine(current_date, slot_time) + 
                              timedelta(minutes=service.duration_minutes)).time()
                    
                    available_times.append({
                        'date': current_date.isoformat(),
                        'start_time': slot_time.strftime('%H:%M'),
                        'end_time': end_time.strftime('%H:%M'),
                        'duration_minutes': service.duration_minutes
                    })
        
        current_date += timedelta(days=1)
    
    return available_times

@booking_bp.route('/bookings', methods=['POST'])
def create_booking():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_id', 'booking_date', 'booking_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        service_id = data['service_id']
        booking_date_str = data['booking_date']
        booking_time_str = data['booking_time']
        
        # Validate service
        service = Service.query.get_or_404(service_id)
        if not service.is_active:
            return jsonify({'error': 'Service not available'}), 400
        
        # Parse date and time
        try:
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            booking_time = datetime.strptime(booking_time_str, '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid date or time format'}), 400
        
        # Check if date is in the future
        if booking_date <= date.today():
            return jsonify({'error': 'Booking date must be in the future'}), 400
        
        # Check if slot is available
        existing_booking = Booking.query.filter_by(
            service_id=service_id,
            booking_date=booking_date,
            booking_time=booking_time,
            status='confirmed'
        ).first()
        
        if existing_booking:
            return jsonify({'error': 'This time slot is already booked'}), 400
        
        # Create booking
        booking = Booking(
            user_id=user.id,
            service_id=service_id,
            booking_date=booking_date,
            booking_time=booking_time,
            duration_minutes=service.duration_minutes,
            price=service.price,
            currency=service.currency,
            notes=data.get('notes', ''),
            status='pending',
            payment_status='pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # TODO: Send confirmation email
        # TODO: Create payment intent for payment processing
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<int:booking_id>/confirm', methods=['POST'])
def confirm_booking(booking_id):
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if user owns this booking or is admin
        if booking.user_id != user.id and user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        payment_id = data.get('payment_id')
        payment_method = data.get('payment_method')
        
        if not payment_id or not payment_method:
            return jsonify({'error': 'Payment information required'}), 400
        
        # Update booking status
        booking.status = 'confirmed'
        booking.payment_status = 'paid'
        booking.payment_id = payment_id
        booking.payment_method = payment_method
        booking.updated_at = datetime.utcnow()
        
        # Generate meeting link if online service
        if booking.service.is_online:
            booking.meeting_link = generate_meeting_link(booking)
            booking.meeting_id = f"meeting_{booking.id}_{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        
        db.session.commit()
        
        # TODO: Send confirmation email with meeting details
        
        return jsonify({
            'message': 'Booking confirmed successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def generate_meeting_link(booking):
    """Generate meeting link for online sessions"""
    # This is a placeholder - in production, integrate with Zoom/Google Meet API
    base_url = "https://meet.google.com/"
    meeting_id = f"omar-ali-{booking.id}-{booking.booking_date.strftime('%Y%m%d')}"
    return f"{base_url}{meeting_id}"

@booking_bp.route('/my-bookings', methods=['GET'])
def get_my_bookings():
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        status_filter = request.args.get('status')
        
        query = Booking.query.filter_by(user_id=user.id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        bookings = query.order_by(Booking.booking_date.desc(), Booking.booking_time.desc()).all()
        
        bookings_data = []
        for booking in bookings:
            booking_dict = booking.to_dict()
            booking_dict['service'] = booking.service.to_dict()
            bookings_data.append(booking_dict)
        
        return jsonify({'bookings': bookings_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if user owns this booking
        if booking.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if booking can be cancelled (e.g., at least 24 hours before)
        booking_datetime = datetime.combine(booking.booking_date, booking.booking_time)
        if booking_datetime <= datetime.now() + timedelta(hours=24):
            return jsonify({'error': 'Cannot cancel booking less than 24 hours before appointment'}), 400
        
        booking.status = 'cancelled'
        booking.updated_at = datetime.utcnow()
        
        # TODO: Process refund if payment was made
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin routes
@booking_bp.route('/admin/services', methods=['POST'])
def create_service():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        required_fields = ['name_ar', 'name_en', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        service = Service(
            name_ar=data['name_ar'],
            name_en=data['name_en'],
            description_ar=data.get('description_ar', ''),
            description_en=data.get('description_en', ''),
            price=data['price'],
            currency=data.get('currency', 'EGP'),
            duration_minutes=data.get('duration_minutes', 60),
            service_type=data.get('service_type', 'healing'),
            is_online=data.get('is_online', False)
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/admin/bookings', methods=['GET'])
def get_all_bookings():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        status_filter = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Booking.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Booking.booking_date >= date_from)
            except ValueError:
                return jsonify({'error': 'Invalid date_from format'}), 400
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Booking.booking_date <= date_to)
            except ValueError:
                return jsonify({'error': 'Invalid date_to format'}), 400
        
        bookings = query.order_by(Booking.booking_date.desc(), Booking.booking_time.desc()).all()
        
        bookings_data = []
        for booking in bookings:
            booking_dict = booking.to_dict()
            booking_dict['service'] = booking.service.to_dict()
            booking_dict['user'] = booking.user.to_dict()
            bookings_data.append(booking_dict)
        
        return jsonify({'bookings': bookings_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/admin/available-slots', methods=['POST'])
def create_available_slot():
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        required_fields = ['date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        try:
            slot_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid date or time format'}), 400
        
        slot = AvailableSlot(
            date=slot_date,
            start_time=start_time,
            end_time=end_time,
            is_recurring=data.get('is_recurring', False),
            recurring_pattern=data.get('recurring_pattern')
        )
        
        db.session.add(slot)
        db.session.commit()
        
        return jsonify({
            'message': 'Available slot created successfully',
            'slot': slot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

