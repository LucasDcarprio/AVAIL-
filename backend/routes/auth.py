from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db
from datetime import datetime
import re

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['username', 'email', 'password', 'real_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 是必填字段'}), 400
    
    # 验证用户名格式
    if not re.match(r'^[a-zA-Z0-9_]+$', data['username']):
        return jsonify({'error': '用户名只能包含字母、数字和下划线'}), 400
    
    # 验证邮箱格式
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 验证密码长度
    if len(data['password']) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 409
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 409
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        real_name=data['real_name'],
        employee_id=data.get('employee_id'),
        department=data.get('department'),
        position=data.get('position'),
        phone=data.get('phone'),
        role='employee'
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功', 'user_id': user.id}), 201

@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    if not user.is_active:
        return jsonify({'error': '账户已被禁用'}), 401
    
    # 创建访问令牌
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'real_name': user.real_name,
            'employee_id': user.employee_id,
            'department': user.department,
            'position': user.position,
            'phone': user.phone,
            'role': user.role
        }
    }), 200

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户资料"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': {
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
        }
    }), 200

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户资料"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新允许的字段
    if data.get('real_name'):
        user.real_name = data['real_name']
    if data.get('phone'):
        user.phone = data['phone']
    if data.get('email'):
        # 检查邮箱是否已被其他用户使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': '邮箱已被其他用户使用'}), 409
        user.email = data['email']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '资料更新成功'}), 200

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': '当前密码和新密码不能为空'}), 400
    
    # 验证当前密码
    if not check_password_hash(user.password, data['current_password']):
        return jsonify({'error': '当前密码错误'}), 401
    
    # 验证新密码长度
    if len(data['new_password']) < 6:
        return jsonify({'error': '新密码长度至少6位'}), 400
    
    # 更新密码
    user.password = generate_password_hash(data['new_password'])
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200