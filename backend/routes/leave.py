from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import LeaveRequest, User, db
from datetime import datetime, date

bp = Blueprint('leave', __name__, url_prefix='/api/leave')

@bp.route('/requests', methods=['GET'])
@jwt_required()
def get_leave_requests():
    """获取请假申请列表"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    if user.role == 'admin':
        # 管理员可以查看所有请假申请
        query = LeaveRequest.query.join(User)
    else:
        # 普通用户只能查看自己的请假申请
        query = LeaveRequest.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter(LeaveRequest.status == status)
    
    query = query.order_by(LeaveRequest.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    requests = pagination.items
    
    return jsonify({
        'requests': [{
            'id': req.id,
            'user_id': req.user_id,
            'username': req.user.username if user.role == 'admin' else None,
            'real_name': req.user.real_name if user.role == 'admin' else None,
            'leave_type': req.leave_type,
            'start_date': req.start_date.strftime('%Y-%m-%d'),
            'end_date': req.end_date.strftime('%Y-%m-%d'),
            'days': req.days,
            'reason': req.reason,
            'status': req.status,
            'approver_id': req.approver_id,
            'approved_at': req.approved_at.strftime('%Y-%m-%d %H:%M:%S') if req.approved_at else None,
            'approval_notes': req.approval_notes,
            'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for req in requests],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@bp.route('/requests', methods=['POST'])
@jwt_required()
def create_leave_request():
    """创建请假申请"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['leave_type', 'start_date', 'end_date', 'reason']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 是必填字段'}), 400
    
    # 解析日期
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式错误，请使用 YYYY-MM-DD 格式'}), 400
    
    # 验证日期
    if start_date > end_date:
        return jsonify({'error': '开始日期不能晚于结束日期'}), 400
    
    if start_date < date.today():
        return jsonify({'error': '开始日期不能早于今天'}), 400
    
    # 计算请假天数
    days = (end_date - start_date).days + 1
    
    # 创建请假申请
    leave_request = LeaveRequest(
        user_id=user_id,
        leave_type=data['leave_type'],
        start_date=start_date,
        end_date=end_date,
        days=days,
        reason=data['reason']
    )
    
    db.session.add(leave_request)
    db.session.commit()
    
    return jsonify({
        'message': '请假申请提交成功',
        'request_id': leave_request.id
    }), 201

@bp.route('/requests/<int:request_id>', methods=['GET'])
@jwt_required()
def get_leave_request(request_id):
    """获取请假申请详情"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    leave_request = LeaveRequest.query.get(request_id)
    if not leave_request:
        return jsonify({'error': '请假申请不存在'}), 404
    
    # 检查权限
    if user.role != 'admin' and leave_request.user_id != user_id:
        return jsonify({'error': '无权访问此请假申请'}), 403
    
    return jsonify({
        'id': leave_request.id,
        'user_id': leave_request.user_id,
        'username': leave_request.user.username,
        'real_name': leave_request.user.real_name,
        'leave_type': leave_request.leave_type,
        'start_date': leave_request.start_date.strftime('%Y-%m-%d'),
        'end_date': leave_request.end_date.strftime('%Y-%m-%d'),
        'days': leave_request.days,
        'reason': leave_request.reason,
        'status': leave_request.status,
        'approver_id': leave_request.approver_id,
        'approved_at': leave_request.approved_at.strftime('%Y-%m-%d %H:%M:%S') if leave_request.approved_at else None,
        'approval_notes': leave_request.approval_notes,
        'created_at': leave_request.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@bp.route('/requests/<int:request_id>', methods=['PUT'])
@jwt_required()
def update_leave_request(request_id):
    """更新请假申请（仅限待审批状态）"""
    user_id = get_jwt_identity()
    
    leave_request = LeaveRequest.query.get(request_id)
    if not leave_request:
        return jsonify({'error': '请假申请不存在'}), 404
    
    # 检查权限
    if leave_request.user_id != user_id:
        return jsonify({'error': '无权修改此请假申请'}), 403
    
    # 检查状态
    if leave_request.status != 'pending':
        return jsonify({'error': '只能修改待审批状态的请假申请'}), 400
    
    data = request.get_json()
    
    # 更新字段
    if 'leave_type' in data:
        leave_request.leave_type = data['leave_type']
    if 'start_date' in data:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        leave_request.start_date = start_date
    if 'end_date' in data:
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        leave_request.end_date = end_date
    if 'reason' in data:
        leave_request.reason = data['reason']
    
    # 重新计算天数
    leave_request.days = (leave_request.end_date - leave_request.start_date).days + 1
    leave_request.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': '请假申请更新成功'}), 200

@bp.route('/requests/<int:request_id>/approve', methods=['POST'])
@jwt_required()
def approve_leave_request(request_id):
    """审批请假申请"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 检查权限
    if user.role not in ['admin', 'manager']:
        return jsonify({'error': '无权审批请假申请'}), 403
    
    leave_request = LeaveRequest.query.get(request_id)
    if not leave_request:
        return jsonify({'error': '请假申请不存在'}), 404
    
    if leave_request.status != 'pending':
        return jsonify({'error': '只能审批待审批状态的请假申请'}), 400
    
    data = request.get_json()
    action = data.get('action')  # 'approve' or 'reject'
    notes = data.get('notes', '')
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': '无效的审批操作'}), 400
    
    # 更新请假申请状态
    leave_request.status = 'approved' if action == 'approve' else 'rejected'
    leave_request.approver_id = user_id
    leave_request.approved_at = datetime.utcnow()
    leave_request.approval_notes = notes
    leave_request.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'请假申请已{"通过" if action == "approve" else "拒绝"}'
    }), 200

@bp.route('/requests/<int:request_id>', methods=['DELETE'])
@jwt_required()
def delete_leave_request(request_id):
    """删除请假申请（仅限待审批状态）"""
    user_id = get_jwt_identity()
    
    leave_request = LeaveRequest.query.get(request_id)
    if not leave_request:
        return jsonify({'error': '请假申请不存在'}), 404
    
    # 检查权限
    if leave_request.user_id != user_id:
        return jsonify({'error': '无权删除此请假申请'}), 403
    
    # 检查状态
    if leave_request.status != 'pending':
        return jsonify({'error': '只能删除待审批状态的请假申请'}), 400
    
    db.session.delete(leave_request)
    db.session.commit()
    
    return jsonify({'message': '请假申请删除成功'}), 200

@bp.route('/types', methods=['GET'])
@jwt_required()
def get_leave_types():
    """获取请假类型列表"""
    leave_types = [
        {'value': 'sick', 'label': '病假'},
        {'value': 'personal', 'label': '事假'},
        {'value': 'annual', 'label': '年假'},
        {'value': 'maternity', 'label': '产假'},
        {'value': 'paternity', 'label': '陪产假'},
        {'value': 'marriage', 'label': '婚假'},
        {'value': 'funeral', 'label': '丧假'},
        {'value': 'other', 'label': '其他'}
    ]
    
    return jsonify({'leave_types': leave_types}), 200