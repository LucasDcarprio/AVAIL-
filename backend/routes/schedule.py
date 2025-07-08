from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Schedule, User, db
from datetime import datetime, date, time, timedelta

bp = Blueprint('schedule', __name__, url_prefix='/api/schedule')

@bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    """获取排班列表"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    schedule_user_id = request.args.get('user_id', type=int)
    
    if user.role == 'admin':
        # 管理员可以查看所有排班
        query = Schedule.query.join(User)
        if schedule_user_id:
            query = query.filter(Schedule.user_id == schedule_user_id)
    else:
        # 普通用户只能查看自己的排班
        query = Schedule.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(Schedule.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Schedule.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    query = query.order_by(Schedule.date.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    schedules = pagination.items
    
    return jsonify({
        'schedules': [{
            'id': schedule.id,
            'user_id': schedule.user_id,
            'username': schedule.user.username if user.role == 'admin' else None,
            'real_name': schedule.user.real_name if user.role == 'admin' else None,
            'date': schedule.date.strftime('%Y-%m-%d'),
            'shift_type': schedule.shift_type,
            'start_time': schedule.start_time.strftime('%H:%M:%S'),
            'end_time': schedule.end_time.strftime('%H:%M:%S'),
            'break_start': schedule.break_start.strftime('%H:%M:%S') if schedule.break_start else None,
            'break_end': schedule.break_end.strftime('%H:%M:%S') if schedule.break_end else None,
            'notes': schedule.notes,
            'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for schedule in schedules],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@bp.route('/schedules', methods=['POST'])
@jwt_required()
def create_schedule():
    """创建排班（管理员功能）"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 检查权限
    if user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['user_id', 'date', 'shift_type', 'start_time', 'end_time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 是必填字段'}), 400
    
    # 验证目标用户是否存在
    target_user = User.query.get(data['user_id'])
    if not target_user:
        return jsonify({'error': '目标用户不存在'}), 404
    
    # 解析日期和时间
    try:
        schedule_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M:%S').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M:%S').time()
    except ValueError:
        return jsonify({'error': '日期时间格式错误'}), 400
    
    # 验证班次类型
    if data['shift_type'] not in ['morning', 'afternoon', 'evening', 'night']:
        return jsonify({'error': '无效的班次类型'}), 400
    
    # 检查当天是否已有排班
    existing_schedule = Schedule.query.filter_by(
        user_id=data['user_id'],
        date=schedule_date
    ).first()
    
    if existing_schedule:
        return jsonify({'error': '当天已有排班'}), 400
    
    # 解析休息时间
    break_start = None
    break_end = None
    if data.get('break_start'):
        break_start = datetime.strptime(data['break_start'], '%H:%M:%S').time()
    if data.get('break_end'):
        break_end = datetime.strptime(data['break_end'], '%H:%M:%S').time()
    
    # 创建排班
    schedule = Schedule(
        user_id=data['user_id'],
        date=schedule_date,
        shift_type=data['shift_type'],
        start_time=start_time,
        end_time=end_time,
        break_start=break_start,
        break_end=break_end,
        notes=data.get('notes')
    )
    
    db.session.add(schedule)
    db.session.commit()
    
    return jsonify({
        'message': '排班创建成功',
        'schedule_id': schedule.id
    }), 201

@bp.route('/schedules/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_schedule(schedule_id):
    """获取排班详情"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({'error': '排班不存在'}), 404
    
    # 检查权限
    if user.role != 'admin' and schedule.user_id != user_id:
        return jsonify({'error': '无权访问此排班'}), 403
    
    return jsonify({
        'id': schedule.id,
        'user_id': schedule.user_id,
        'username': schedule.user.username,
        'real_name': schedule.user.real_name,
        'date': schedule.date.strftime('%Y-%m-%d'),
        'shift_type': schedule.shift_type,
        'start_time': schedule.start_time.strftime('%H:%M:%S'),
        'end_time': schedule.end_time.strftime('%H:%M:%S'),
        'break_start': schedule.break_start.strftime('%H:%M:%S') if schedule.break_start else None,
        'break_end': schedule.break_end.strftime('%H:%M:%S') if schedule.break_end else None,
        'notes': schedule.notes,
        'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    """更新排班（管理员功能）"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 检查权限
    if user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({'error': '排班不存在'}), 404
    
    data = request.get_json()
    
    # 更新字段
    if 'shift_type' in data:
        if data['shift_type'] not in ['morning', 'afternoon', 'evening', 'night']:
            return jsonify({'error': '无效的班次类型'}), 400
        schedule.shift_type = data['shift_type']
    
    if 'start_time' in data:
        start_time = datetime.strptime(data['start_time'], '%H:%M:%S').time()
        schedule.start_time = start_time
    
    if 'end_time' in data:
        end_time = datetime.strptime(data['end_time'], '%H:%M:%S').time()
        schedule.end_time = end_time
    
    if 'break_start' in data:
        if data['break_start']:
            schedule.break_start = datetime.strptime(data['break_start'], '%H:%M:%S').time()
        else:
            schedule.break_start = None
    
    if 'break_end' in data:
        if data['break_end']:
            schedule.break_end = datetime.strptime(data['break_end'], '%H:%M:%S').time()
        else:
            schedule.break_end = None
    
    if 'notes' in data:
        schedule.notes = data['notes']
    
    schedule.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': '排班更新成功'}), 200

@bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_schedule(schedule_id):
    """删除排班（管理员功能）"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 检查权限
    if user.role != 'admin':
        return jsonify({'error': '需要管理员权限'}), 403
    
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({'error': '排班不存在'}), 404
    
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({'message': '排班删除成功'}), 200

@bp.route('/my-schedule', methods=['GET'])
@jwt_required()
def get_my_schedule():
    """获取我的排班"""
    user_id = get_jwt_identity()
    
    # 获取查询参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 默认查询当前月份的排班
    if not start_date:
        start_date = date.today().replace(day=1).strftime('%Y-%m-%d')
    if not end_date:
        # 获取当前月份的最后一天
        today = date.today()
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        end_date = (next_month - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 查询排班
    schedules = Schedule.query.filter_by(user_id=user_id).filter(
        Schedule.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
        Schedule.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
    ).order_by(Schedule.date).all()
    
    return jsonify({
        'schedules': [{
            'id': schedule.id,
            'date': schedule.date.strftime('%Y-%m-%d'),
            'shift_type': schedule.shift_type,
            'start_time': schedule.start_time.strftime('%H:%M:%S'),
            'end_time': schedule.end_time.strftime('%H:%M:%S'),
            'break_start': schedule.break_start.strftime('%H:%M:%S') if schedule.break_start else None,
            'break_end': schedule.break_end.strftime('%H:%M:%S') if schedule.break_end else None,
            'notes': schedule.notes
        } for schedule in schedules],
        'period': {
            'start_date': start_date,
            'end_date': end_date
        }
    }), 200

@bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_schedule():
    """获取今天的排班"""
    user_id = get_jwt_identity()
    today = date.today()
    
    schedule = Schedule.query.filter_by(
        user_id=user_id,
        date=today
    ).first()
    
    if not schedule:
        return jsonify({'schedule': None}), 200
    
    return jsonify({
        'schedule': {
            'id': schedule.id,
            'date': schedule.date.strftime('%Y-%m-%d'),
            'shift_type': schedule.shift_type,
            'start_time': schedule.start_time.strftime('%H:%M:%S'),
            'end_time': schedule.end_time.strftime('%H:%M:%S'),
            'break_start': schedule.break_start.strftime('%H:%M:%S') if schedule.break_start else None,
            'break_end': schedule.break_end.strftime('%H:%M:%S') if schedule.break_end else None,
            'notes': schedule.notes
        }
    }), 200

@bp.route('/shift-types', methods=['GET'])
@jwt_required()
def get_shift_types():
    """获取班次类型列表"""
    shift_types = [
        {'value': 'morning', 'label': '早班'},
        {'value': 'afternoon', 'label': '中班'},
        {'value': 'evening', 'label': '晚班'},
        {'value': 'night', 'label': '夜班'}
    ]
    
    return jsonify({'shift_types': shift_types}), 200

@bp.route('/calendar', methods=['GET'])
@jwt_required()
def get_schedule_calendar():
    """获取排班日历视图"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # 解析月份
    year, month_num = map(int, month.split('-'))
    
    # 获取当月的排班
    if user.role == 'admin':
        # 管理员可以查看所有人的排班
        schedules = Schedule.query.join(User).filter(
            db.extract('year', Schedule.date) == year,
            db.extract('month', Schedule.date) == month_num
        ).all()
    else:
        # 普通用户只能查看自己的排班
        schedules = Schedule.query.filter_by(user_id=user_id).filter(
            db.extract('year', Schedule.date) == year,
            db.extract('month', Schedule.date) == month_num
        ).all()
    
    # 构建日历数据
    calendar_data = {}
    for schedule in schedules:
        date_str = schedule.date.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        
        schedule_info = {
            'id': schedule.id,
            'shift_type': schedule.shift_type,
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'notes': schedule.notes
        }
        
        if user.role == 'admin':
            schedule_info.update({
                'user_id': schedule.user_id,
                'username': schedule.user.username,
                'real_name': schedule.user.real_name
            })
        
        calendar_data[date_str].append(schedule_info)
    
    return jsonify({
        'month': month,
        'calendar': calendar_data
    }), 200