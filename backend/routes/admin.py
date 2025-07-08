from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, SystemSettings, AttendanceRecord, db
from datetime import datetime, date
from werkzeug.security import generate_password_hash

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(func):
    """管理员权限装饰器"""
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(
            User.username.contains(search) |
            User.real_name.contains(search) |
            User.email.contains(search)
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'real_name': user.real_name,
            'employee_id': user.employee_id,
            'department': user.department,
            'position': user.position,
            'phone': user.phone,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None
        } for user in users],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """创建用户"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['username', 'email', 'password', 'real_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 是必填字段'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 409
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 409
    
    # 创建用户
    user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        real_name=data['real_name'],
        employee_id=data.get('employee_id'),
        department=data.get('department'),
        position=data.get('position'),
        phone=data.get('phone'),
        role=data.get('role', 'employee'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '用户创建成功', 'user_id': user.id}), 201

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新字段
    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'employee_id' in data:
        user.employee_id = data['employee_id']
    if 'department' in data:
        user.department = data['department']
    if 'position' in data:
        user.position = data['position']
    if 'phone' in data:
        user.phone = data['phone']
    if 'role' in data:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'email' in data:
        # 检查邮箱是否已被其他用户使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': '邮箱已被其他用户使用'}), 409
        user.email = data['email']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '用户信息更新成功'}), 200

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 不能删除管理员
    if user.role == 'admin':
        return jsonify({'error': '不能删除管理员用户'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户删除成功'}), 200

@bp.route('/settings', methods=['GET'])
@jwt_required()
@admin_required
def get_settings():
    """获取系统设置"""
    settings = SystemSettings.query.all()
    return jsonify({
        'settings': [{
            'key': setting.key,
            'value': setting.value,
            'description': setting.description
        } for setting in settings]
    }), 200

@bp.route('/settings', methods=['POST'])
@jwt_required()
@admin_required
def update_settings():
    """更新系统设置"""
    data = request.get_json()
    
    for key, value in data.items():
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(key=key, value=value)
            db.session.add(setting)
    
    db.session.commit()
    
    return jsonify({'message': '设置更新成功'}), 200

@bp.route('/attendance/records', methods=['GET'])
@jwt_required()
@admin_required
def get_attendance_records():
    """获取所有考勤记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id', type=int)
    
    query = AttendanceRecord.query.join(User)
    
    if start_date:
        query = query.filter(AttendanceRecord.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(AttendanceRecord.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if user_id:
        query = query.filter(AttendanceRecord.user_id == user_id)
    
    query = query.order_by(AttendanceRecord.date.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    
    return jsonify({
        'records': [{
            'id': record.id,
            'user_id': record.user_id,
            'username': record.user.username,
            'real_name': record.user.real_name,
            'date': record.date.strftime('%Y-%m-%d'),
            'clock_in_time': record.clock_in_time.strftime('%Y-%m-%d %H:%M:%S') if record.clock_in_time else None,
            'clock_out_time': record.clock_out_time.strftime('%Y-%m-%d %H:%M:%S') if record.clock_out_time else None,
            'work_hours': record.work_hours,
            'status': record.status,
            'notes': record.notes
        } for record in records],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@bp.route('/attendance/statistics', methods=['GET'])
@jwt_required()
@admin_required
def attendance_statistics():
    """获取考勤统计"""
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # 解析月份
    year, month_num = map(int, month.split('-'))
    
    # 获取当月考勤记录
    records = AttendanceRecord.query.filter(
        db.extract('year', AttendanceRecord.date) == year,
        db.extract('month', AttendanceRecord.date) == month_num
    ).all()
    
    # 统计数据
    total_records = len(records)
    total_work_hours = sum(record.work_hours for record in records)
    normal_count = len([r for r in records if r.status == 'normal'])
    late_count = len([r for r in records if r.status == 'late'])
    early_leave_count = len([r for r in records if r.status == 'early_leave'])
    absent_count = len([r for r in records if r.status == 'absent'])
    
    return jsonify({
        'month': month,
        'total_records': total_records,
        'total_work_hours': round(total_work_hours, 2),
        'normal_count': normal_count,
        'late_count': late_count,
        'early_leave_count': early_leave_count,
        'absent_count': absent_count
    }), 200