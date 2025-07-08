from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import OutingReport, User, db
from datetime import datetime

bp = Blueprint('outing', __name__, url_prefix='/api/outing')

@bp.route('/reports', methods=['GET'])
@jwt_required()
def get_outing_reports():
    """获取外出报备列表"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    if user.role == 'admin':
        # 管理员可以查看所有外出报备
        query = OutingReport.query.join(User)
    else:
        # 普通用户只能查看自己的外出报备
        query = OutingReport.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter(OutingReport.status == status)
    
    query = query.order_by(OutingReport.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    reports = pagination.items
    
    return jsonify({
        'reports': [{
            'id': report.id,
            'user_id': report.user_id,
            'username': report.user.username if user.role == 'admin' else None,
            'real_name': report.user.real_name if user.role == 'admin' else None,
            'destination': report.destination,
            'purpose': report.purpose,
            'start_time': report.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'expected_return_time': report.expected_return_time.strftime('%Y-%m-%d %H:%M:%S'),
            'actual_return_time': report.actual_return_time.strftime('%Y-%m-%d %H:%M:%S') if report.actual_return_time else None,
            'contact_info': report.contact_info,
            'status': report.status,
            'approver_id': report.approver_id,
            'approved_at': report.approved_at.strftime('%Y-%m-%d %H:%M:%S') if report.approved_at else None,
            'approval_notes': report.approval_notes,
            'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for report in reports],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@bp.route('/reports', methods=['POST'])
@jwt_required()
def create_outing_report():
    """创建外出报备"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['destination', 'purpose', 'start_time', 'expected_return_time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 是必填字段'}), 400
    
    # 解析时间
    try:
        start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
        expected_return_time = datetime.strptime(data['expected_return_time'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': '时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式'}), 400
    
    # 验证时间
    if start_time >= expected_return_time:
        return jsonify({'error': '预计返回时间必须晚于外出时间'}), 400
    
    if start_time < datetime.now():
        return jsonify({'error': '外出时间不能早于当前时间'}), 400
    
    # 创建外出报备
    outing_report = OutingReport(
        user_id=user_id,
        destination=data['destination'],
        purpose=data['purpose'],
        start_time=start_time,
        expected_return_time=expected_return_time,
        contact_info=data.get('contact_info')
    )
    
    db.session.add(outing_report)
    db.session.commit()
    
    return jsonify({
        'message': '外出报备提交成功',
        'report_id': outing_report.id
    }), 201

@bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_outing_report(report_id):
    """获取外出报备详情"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    outing_report = OutingReport.query.get(report_id)
    if not outing_report:
        return jsonify({'error': '外出报备不存在'}), 404
    
    # 检查权限
    if user.role != 'admin' and outing_report.user_id != user_id:
        return jsonify({'error': '无权访问此外出报备'}), 403
    
    return jsonify({
        'id': outing_report.id,
        'user_id': outing_report.user_id,
        'username': outing_report.user.username,
        'real_name': outing_report.user.real_name,
        'destination': outing_report.destination,
        'purpose': outing_report.purpose,
        'start_time': outing_report.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'expected_return_time': outing_report.expected_return_time.strftime('%Y-%m-%d %H:%M:%S'),
        'actual_return_time': outing_report.actual_return_time.strftime('%Y-%m-%d %H:%M:%S') if outing_report.actual_return_time else None,
        'contact_info': outing_report.contact_info,
        'status': outing_report.status,
        'approver_id': outing_report.approver_id,
        'approved_at': outing_report.approved_at.strftime('%Y-%m-%d %H:%M:%S') if outing_report.approved_at else None,
        'approval_notes': outing_report.approval_notes,
        'created_at': outing_report.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@bp.route('/reports/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_outing_report(report_id):
    """更新外出报备（仅限待审批状态）"""
    user_id = get_jwt_identity()
    
    outing_report = OutingReport.query.get(report_id)
    if not outing_report:
        return jsonify({'error': '外出报备不存在'}), 404
    
    # 检查权限
    if outing_report.user_id != user_id:
        return jsonify({'error': '无权修改此外出报备'}), 403
    
    # 检查状态
    if outing_report.status != 'pending':
        return jsonify({'error': '只能修改待审批状态的外出报备'}), 400
    
    data = request.get_json()
    
    # 更新字段
    if 'destination' in data:
        outing_report.destination = data['destination']
    if 'purpose' in data:
        outing_report.purpose = data['purpose']
    if 'start_time' in data:
        start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
        outing_report.start_time = start_time
    if 'expected_return_time' in data:
        expected_return_time = datetime.strptime(data['expected_return_time'], '%Y-%m-%d %H:%M:%S')
        outing_report.expected_return_time = expected_return_time
    if 'contact_info' in data:
        outing_report.contact_info = data['contact_info']
    
    # 验证时间
    if outing_report.start_time >= outing_report.expected_return_time:
        return jsonify({'error': '预计返回时间必须晚于外出时间'}), 400
    
    outing_report.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': '外出报备更新成功'}), 200

@bp.route('/reports/<int:report_id>/approve', methods=['POST'])
@jwt_required()
def approve_outing_report(report_id):
    """审批外出报备"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 检查权限
    if user.role not in ['admin', 'manager']:
        return jsonify({'error': '无权审批外出报备'}), 403
    
    outing_report = OutingReport.query.get(report_id)
    if not outing_report:
        return jsonify({'error': '外出报备不存在'}), 404
    
    if outing_report.status != 'pending':
        return jsonify({'error': '只能审批待审批状态的外出报备'}), 400
    
    data = request.get_json()
    action = data.get('action')  # 'approve' or 'reject'
    notes = data.get('notes', '')
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': '无效的审批操作'}), 400
    
    # 更新外出报备状态
    outing_report.status = 'approved' if action == 'approve' else 'rejected'
    outing_report.approver_id = user_id
    outing_report.approved_at = datetime.utcnow()
    outing_report.approval_notes = notes
    outing_report.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'外出报备已{"通过" if action == "approve" else "拒绝"}'
    }), 200

@bp.route('/reports/<int:report_id>/complete', methods=['POST'])
@jwt_required()
def complete_outing_report(report_id):
    """完成外出报备（返回）"""
    user_id = get_jwt_identity()
    
    outing_report = OutingReport.query.get(report_id)
    if not outing_report:
        return jsonify({'error': '外出报备不存在'}), 404
    
    # 检查权限
    if outing_report.user_id != user_id:
        return jsonify({'error': '无权操作此外出报备'}), 403
    
    # 检查状态
    if outing_report.status != 'approved':
        return jsonify({'error': '只能完成已审批的外出报备'}), 400
    
    if outing_report.actual_return_time:
        return jsonify({'error': '外出报备已完成'}), 400
    
    # 更新实际返回时间
    outing_report.actual_return_time = datetime.utcnow()
    outing_report.status = 'completed'
    outing_report.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': '外出报备完成'}), 200

@bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_outing_report(report_id):
    """删除外出报备（仅限待审批状态）"""
    user_id = get_jwt_identity()
    
    outing_report = OutingReport.query.get(report_id)
    if not outing_report:
        return jsonify({'error': '外出报备不存在'}), 404
    
    # 检查权限
    if outing_report.user_id != user_id:
        return jsonify({'error': '无权删除此外出报备'}), 403
    
    # 检查状态
    if outing_report.status != 'pending':
        return jsonify({'error': '只能删除待审批状态的外出报备'}), 400
    
    db.session.delete(outing_report)
    db.session.commit()
    
    return jsonify({'message': '外出报备删除成功'}), 200

@bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_outing():
    """获取当前进行中的外出报备"""
    user_id = get_jwt_identity()
    
    # 查找已审批但未完成的外出报备
    current_outing = OutingReport.query.filter_by(
        user_id=user_id,
        status='approved'
    ).filter(
        OutingReport.actual_return_time.is_(None)
    ).filter(
        OutingReport.start_time <= datetime.utcnow()
    ).first()
    
    if not current_outing:
        return jsonify({'outing': None}), 200
    
    return jsonify({
        'outing': {
            'id': current_outing.id,
            'destination': current_outing.destination,
            'purpose': current_outing.purpose,
            'start_time': current_outing.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'expected_return_time': current_outing.expected_return_time.strftime('%Y-%m-%d %H:%M:%S'),
            'contact_info': current_outing.contact_info,
            'status': current_outing.status
        }
    }), 200