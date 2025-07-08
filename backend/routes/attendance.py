from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import AttendanceRecord, User, SystemSettings, db
from datetime import datetime, date, time
import ipaddress

bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@bp.route('/clock-in', methods=['POST'])
@jwt_required()
def clock_in():
    """上班打卡"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    today = date.today()
    current_time = datetime.now()
    
    # 检查今天是否已经打过上班卡
    existing_record = AttendanceRecord.query.filter_by(
        user_id=user_id, 
        date=today
    ).first()
    
    if existing_record and existing_record.clock_in_time:
        return jsonify({'error': '今天已经打过上班卡'}), 400
    
    # 获取工作时间设置
    work_start_time = get_system_setting('work_start_time', '09:00')
    work_hours = datetime.strptime(work_start_time, '%H:%M').time()
    
    # 判断是否迟到
    status = 'normal'
    if current_time.time() > work_hours:
        status = 'late'
    
    # 创建或更新考勤记录
    if existing_record:
        existing_record.clock_in_time = current_time
        existing_record.clock_in_ip = request.remote_addr
        existing_record.status = status
        existing_record.updated_at = datetime.utcnow()
        record = existing_record
    else:
        record = AttendanceRecord(
            user_id=user_id,
            date=today,
            clock_in_time=current_time,
            clock_in_ip=request.remote_addr,
            status=status
        )
        db.session.add(record)
    
    db.session.commit()
    
    return jsonify({
        'message': '上班打卡成功',
        'clock_in_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'status': status
    }), 200

@bp.route('/clock-out', methods=['POST'])
@jwt_required()
def clock_out():
    """下班打卡"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    today = date.today()
    current_time = datetime.now()
    
    # 查找今天的考勤记录
    record = AttendanceRecord.query.filter_by(
        user_id=user_id, 
        date=today
    ).first()
    
    if not record:
        return jsonify({'error': '请先进行上班打卡'}), 400
    
    if not record.clock_in_time:
        return jsonify({'error': '请先进行上班打卡'}), 400
    
    if record.clock_out_time:
        return jsonify({'error': '今天已经打过下班卡'}), 400
    
    # 获取工作时间设置
    work_end_time = get_system_setting('work_end_time', '18:00')
    work_end_hours = datetime.strptime(work_end_time, '%H:%M').time()
    
    # 计算工作时长
    work_duration = current_time - record.clock_in_time
    work_hours = work_duration.total_seconds() / 3600
    
    # 扣除休息时间
    break_duration = float(get_system_setting('break_duration', '1.0'))
    work_hours -= break_duration
    
    # 判断是否早退
    if current_time.time() < work_end_hours:
        record.status = 'early_leave'
    
    # 更新考勤记录
    record.clock_out_time = current_time
    record.clock_out_ip = request.remote_addr
    record.work_hours = round(work_hours, 2)
    record.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': '下班打卡成功',
        'clock_out_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'work_hours': round(work_hours, 2),
        'status': record.status
    }), 200

@bp.route('/today', methods=['GET'])
@jwt_required()
def today_attendance():
    """获取今天的考勤记录"""
    user_id = get_jwt_identity()
    today = date.today()
    
    record = AttendanceRecord.query.filter_by(
        user_id=user_id, 
        date=today
    ).first()
    
    if not record:
        return jsonify({
            'date': today.strftime('%Y-%m-%d'),
            'clock_in_time': None,
            'clock_out_time': None,
            'work_hours': 0,
            'status': 'not_clocked_in'
        }), 200
    
    return jsonify({
        'date': record.date.strftime('%Y-%m-%d'),
        'clock_in_time': record.clock_in_time.strftime('%Y-%m-%d %H:%M:%S') if record.clock_in_time else None,
        'clock_out_time': record.clock_out_time.strftime('%Y-%m-%d %H:%M:%S') if record.clock_out_time else None,
        'work_hours': record.work_hours,
        'status': record.status,
        'notes': record.notes
    }), 200

@bp.route('/history', methods=['GET'])
@jwt_required()
def attendance_history():
    """获取考勤历史记录"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AttendanceRecord.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(AttendanceRecord.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(AttendanceRecord.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    query = query.order_by(AttendanceRecord.date.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    
    return jsonify({
        'records': [{
            'id': record.id,
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

@bp.route('/statistics', methods=['GET'])
@jwt_required()
def attendance_statistics():
    """获取考勤统计"""
    user_id = get_jwt_identity()
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # 解析月份
    year, month_num = map(int, month.split('-'))
    
    # 获取当月考勤记录
    records = AttendanceRecord.query.filter_by(user_id=user_id).filter(
        db.extract('year', AttendanceRecord.date) == year,
        db.extract('month', AttendanceRecord.date) == month_num
    ).all()
    
    # 统计数据
    total_days = len(records)
    total_work_hours = sum(record.work_hours for record in records)
    normal_days = len([r for r in records if r.status == 'normal'])
    late_days = len([r for r in records if r.status == 'late'])
    early_leave_days = len([r for r in records if r.status == 'early_leave'])
    absent_days = len([r for r in records if r.status == 'absent'])
    
    return jsonify({
        'month': month,
        'total_days': total_days,
        'total_work_hours': round(total_work_hours, 2),
        'normal_days': normal_days,
        'late_days': late_days,
        'early_leave_days': early_leave_days,
        'absent_days': absent_days
    }), 200

def get_system_setting(key, default_value):
    """获取系统设置"""
    setting = SystemSettings.query.filter_by(key=key).first()
    return setting.value if setting else default_value