from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import WorkDiary, User, db
from datetime import datetime, date

bp = Blueprint('diary', __name__, url_prefix='/api/diary')

@bp.route('/diaries', methods=['GET'])
@jwt_required()
def get_work_diaries():
    """获取工作日报列表"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if user.role == 'admin':
        # 管理员可以查看所有工作日报
        query = WorkDiary.query.join(User)
    else:
        # 普通用户只能查看自己的工作日报
        query = WorkDiary.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(WorkDiary.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(WorkDiary.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    query = query.order_by(WorkDiary.date.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    diaries = pagination.items
    
    return jsonify({
        'diaries': [{
            'id': diary.id,
            'user_id': diary.user_id,
            'username': diary.user.username if user.role == 'admin' else None,
            'real_name': diary.user.real_name if user.role == 'admin' else None,
            'date': diary.date.strftime('%Y-%m-%d'),
            'content': diary.content,
            'achievements': diary.achievements,
            'issues': diary.issues,
            'next_plan': diary.next_plan,
            'created_at': diary.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for diary in diaries],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@bp.route('/diaries', methods=['POST'])
@jwt_required()
def create_work_diary():
    """创建工作日报"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['date', 'content']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 是必填字段'}), 400
    
    # 解析日期
    try:
        diary_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式错误，请使用 YYYY-MM-DD 格式'}), 400
    
    # 验证日期
    if diary_date > date.today():
        return jsonify({'error': '日报日期不能晚于今天'}), 400
    
    # 检查当天是否已有日报
    existing_diary = WorkDiary.query.filter_by(
        user_id=user_id,
        date=diary_date
    ).first()
    
    if existing_diary:
        return jsonify({'error': '当天已有工作日报'}), 400
    
    # 创建工作日报
    work_diary = WorkDiary(
        user_id=user_id,
        date=diary_date,
        content=data['content'],
        achievements=data.get('achievements'),
        issues=data.get('issues'),
        next_plan=data.get('next_plan')
    )
    
    db.session.add(work_diary)
    db.session.commit()
    
    return jsonify({
        'message': '工作日报创建成功',
        'diary_id': work_diary.id
    }), 201

@bp.route('/diaries/<int:diary_id>', methods=['GET'])
@jwt_required()
def get_work_diary(diary_id):
    """获取工作日报详情"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    work_diary = WorkDiary.query.get(diary_id)
    if not work_diary:
        return jsonify({'error': '工作日报不存在'}), 404
    
    # 检查权限
    if user.role != 'admin' and work_diary.user_id != user_id:
        return jsonify({'error': '无权访问此工作日报'}), 403
    
    return jsonify({
        'id': work_diary.id,
        'user_id': work_diary.user_id,
        'username': work_diary.user.username,
        'real_name': work_diary.user.real_name,
        'date': work_diary.date.strftime('%Y-%m-%d'),
        'content': work_diary.content,
        'achievements': work_diary.achievements,
        'issues': work_diary.issues,
        'next_plan': work_diary.next_plan,
        'created_at': work_diary.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@bp.route('/diaries/<int:diary_id>', methods=['PUT'])
@jwt_required()
def update_work_diary(diary_id):
    """更新工作日报"""
    user_id = get_jwt_identity()
    
    work_diary = WorkDiary.query.get(diary_id)
    if not work_diary:
        return jsonify({'error': '工作日报不存在'}), 404
    
    # 检查权限
    if work_diary.user_id != user_id:
        return jsonify({'error': '无权修改此工作日报'}), 403
    
    # 检查是否是当天的日报
    if work_diary.date != date.today():
        return jsonify({'error': '只能修改当天的工作日报'}), 400
    
    data = request.get_json()
    
    # 更新字段
    if 'content' in data:
        work_diary.content = data['content']
    if 'achievements' in data:
        work_diary.achievements = data['achievements']
    if 'issues' in data:
        work_diary.issues = data['issues']
    if 'next_plan' in data:
        work_diary.next_plan = data['next_plan']
    
    work_diary.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': '工作日报更新成功'}), 200

@bp.route('/diaries/<int:diary_id>', methods=['DELETE'])
@jwt_required()
def delete_work_diary(diary_id):
    """删除工作日报"""
    user_id = get_jwt_identity()
    
    work_diary = WorkDiary.query.get(diary_id)
    if not work_diary:
        return jsonify({'error': '工作日报不存在'}), 404
    
    # 检查权限
    if work_diary.user_id != user_id:
        return jsonify({'error': '无权删除此工作日报'}), 403
    
    # 检查是否是当天的日报
    if work_diary.date != date.today():
        return jsonify({'error': '只能删除当天的工作日报'}), 400
    
    db.session.delete(work_diary)
    db.session.commit()
    
    return jsonify({'message': '工作日报删除成功'}), 200

@bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_diary():
    """获取今天的工作日报"""
    user_id = get_jwt_identity()
    today = date.today()
    
    work_diary = WorkDiary.query.filter_by(
        user_id=user_id,
        date=today
    ).first()
    
    if not work_diary:
        return jsonify({'diary': None}), 200
    
    return jsonify({
        'diary': {
            'id': work_diary.id,
            'date': work_diary.date.strftime('%Y-%m-%d'),
            'content': work_diary.content,
            'achievements': work_diary.achievements,
            'issues': work_diary.issues,
            'next_plan': work_diary.next_plan,
            'created_at': work_diary.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    }), 200

@bp.route('/statistics', methods=['GET'])
@jwt_required()
def diary_statistics():
    """获取日报统计"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # 解析月份
    year, month_num = map(int, month.split('-'))
    
    # 查询条件
    query = WorkDiary.query.filter(
        db.extract('year', WorkDiary.date) == year,
        db.extract('month', WorkDiary.date) == month_num
    )
    
    if user.role != 'admin':
        query = query.filter_by(user_id=user_id)
    
    diaries = query.all()
    
    # 统计数据
    total_diaries = len(diaries)
    
    # 按用户统计（管理员可见）
    user_statistics = {}
    if user.role == 'admin':
        for diary in diaries:
            username = diary.user.username
            if username not in user_statistics:
                user_statistics[username] = {
                    'real_name': diary.user.real_name,
                    'count': 0
                }
            user_statistics[username]['count'] += 1
    
    return jsonify({
        'month': month,
        'total_diaries': total_diaries,
        'user_statistics': user_statistics if user.role == 'admin' else None
    }), 200