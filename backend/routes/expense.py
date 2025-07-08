from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import ExpenseReport, User, db
from datetime import datetime, date

bp = Blueprint('expense', __name__, url_prefix='/api/expense')

@bp.route('/reports', methods=['GET'])
@jwt_required()
def get_expense_reports():
    """获取费用报销列表"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    if user.role == 'admin':
        # 管理员可以查看所有费用报销
        query = ExpenseReport.query.join(User)
    else:
        # 普通用户只能查看自己的费用报销
        query = ExpenseReport.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter(ExpenseReport.status == status)
    
    query = query.order_by(ExpenseReport.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    reports = pagination.items
    
    return jsonify({
        'reports': [{
            'id': report.id,
            'user_id': report.user_id,
            'username': report.user.username if user.role == 'admin' else None,
            'real_name': report.user.real_name if user.role == 'admin' else None,
            'expense_type': report.expense_type,
            'amount': report.amount,
            'date': report.date.strftime('%Y-%m-%d'),
            'description': report.description,
            'receipt_url': report.receipt_url,
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
def create_expense_report():
    """创建费用报销"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['expense_type', 'amount', 'date', 'description']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 是必填字段'}), 400
    
    # 验证金额
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': '金额必须大于0'}), 400
    except ValueError:
        return jsonify({'error': '金额格式错误'}), 400
    
    # 解析日期
    try:
        expense_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式错误，请使用 YYYY-MM-DD 格式'}), 400
    
    # 验证日期
    if expense_date > date.today():
        return jsonify({'error': '费用日期不能晚于今天'}), 400
    
    # 创建费用报销
    expense_report = ExpenseReport(
        user_id=user_id,
        expense_type=data['expense_type'],
        amount=amount,
        date=expense_date,
        description=data['description'],
        receipt_url=data.get('receipt_url')
    )
    
    db.session.add(expense_report)
    db.session.commit()
    
    return jsonify({
        'message': '费用报销提交成功',
        'report_id': expense_report.id
    }), 201

@bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_expense_report(report_id):
    """获取费用报销详情"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    expense_report = ExpenseReport.query.get(report_id)
    if not expense_report:
        return jsonify({'error': '费用报销不存在'}), 404
    
    # 检查权限
    if user.role != 'admin' and expense_report.user_id != user_id:
        return jsonify({'error': '无权访问此费用报销'}), 403
    
    return jsonify({
        'id': expense_report.id,
        'user_id': expense_report.user_id,
        'username': expense_report.user.username,
        'real_name': expense_report.user.real_name,
        'expense_type': expense_report.expense_type,
        'amount': expense_report.amount,
        'date': expense_report.date.strftime('%Y-%m-%d'),
        'description': expense_report.description,
        'receipt_url': expense_report.receipt_url,
        'status': expense_report.status,
        'approver_id': expense_report.approver_id,
        'approved_at': expense_report.approved_at.strftime('%Y-%m-%d %H:%M:%S') if expense_report.approved_at else None,
        'approval_notes': expense_report.approval_notes,
        'created_at': expense_report.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@bp.route('/reports/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_expense_report(report_id):
    """更新费用报销（仅限待审批状态）"""
    user_id = get_jwt_identity()
    
    expense_report = ExpenseReport.query.get(report_id)
    if not expense_report:
        return jsonify({'error': '费用报销不存在'}), 404
    
    # 检查权限
    if expense_report.user_id != user_id:
        return jsonify({'error': '无权修改此费用报销'}), 403
    
    # 检查状态
    if expense_report.status != 'pending':
        return jsonify({'error': '只能修改待审批状态的费用报销'}), 400
    
    data = request.get_json()
    
    # 更新字段
    if 'expense_type' in data:
        expense_report.expense_type = data['expense_type']
    if 'amount' in data:
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': '金额必须大于0'}), 400
            expense_report.amount = amount
        except ValueError:
            return jsonify({'error': '金额格式错误'}), 400
    if 'date' in data:
        expense_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        expense_report.date = expense_date
    if 'description' in data:
        expense_report.description = data['description']
    if 'receipt_url' in data:
        expense_report.receipt_url = data['receipt_url']
    
    expense_report.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': '费用报销更新成功'}), 200

@bp.route('/reports/<int:report_id>/approve', methods=['POST'])
@jwt_required()
def approve_expense_report(report_id):
    """审批费用报销"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 检查权限
    if user.role not in ['admin', 'manager']:
        return jsonify({'error': '无权审批费用报销'}), 403
    
    expense_report = ExpenseReport.query.get(report_id)
    if not expense_report:
        return jsonify({'error': '费用报销不存在'}), 404
    
    if expense_report.status != 'pending':
        return jsonify({'error': '只能审批待审批状态的费用报销'}), 400
    
    data = request.get_json()
    action = data.get('action')  # 'approve' or 'reject'
    notes = data.get('notes', '')
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': '无效的审批操作'}), 400
    
    # 更新费用报销状态
    expense_report.status = 'approved' if action == 'approve' else 'rejected'
    expense_report.approver_id = user_id
    expense_report.approved_at = datetime.utcnow()
    expense_report.approval_notes = notes
    expense_report.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'费用报销已{"通过" if action == "approve" else "拒绝"}'
    }), 200

@bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_expense_report(report_id):
    """删除费用报销（仅限待审批状态）"""
    user_id = get_jwt_identity()
    
    expense_report = ExpenseReport.query.get(report_id)
    if not expense_report:
        return jsonify({'error': '费用报销不存在'}), 404
    
    # 检查权限
    if expense_report.user_id != user_id:
        return jsonify({'error': '无权删除此费用报销'}), 403
    
    # 检查状态
    if expense_report.status != 'pending':
        return jsonify({'error': '只能删除待审批状态的费用报销'}), 400
    
    db.session.delete(expense_report)
    db.session.commit()
    
    return jsonify({'message': '费用报销删除成功'}), 200

@bp.route('/types', methods=['GET'])
@jwt_required()
def get_expense_types():
    """获取费用类型列表"""
    expense_types = [
        {'value': 'travel', 'label': '差旅费'},
        {'value': 'meal', 'label': '餐费'},
        {'value': 'transportation', 'label': '交通费'},
        {'value': 'accommodation', 'label': '住宿费'},
        {'value': 'office', 'label': '办公用品'},
        {'value': 'communication', 'label': '通讯费'},
        {'value': 'training', 'label': '培训费'},
        {'value': 'entertainment', 'label': '招待费'},
        {'value': 'other', 'label': '其他'}
    ]
    
    return jsonify({'expense_types': expense_types}), 200

@bp.route('/statistics', methods=['GET'])
@jwt_required()
def expense_statistics():
    """获取费用统计"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # 解析月份
    year, month_num = map(int, month.split('-'))
    
    # 查询条件
    query = ExpenseReport.query.filter(
        db.extract('year', ExpenseReport.date) == year,
        db.extract('month', ExpenseReport.date) == month_num
    )
    
    if user.role != 'admin':
        query = query.filter_by(user_id=user_id)
    
    reports = query.all()
    
    # 统计数据
    total_amount = sum(report.amount for report in reports)
    approved_amount = sum(report.amount for report in reports if report.status == 'approved')
    pending_amount = sum(report.amount for report in reports if report.status == 'pending')
    rejected_amount = sum(report.amount for report in reports if report.status == 'rejected')
    
    # 按类型统计
    type_statistics = {}
    for report in reports:
        if report.expense_type not in type_statistics:
            type_statistics[report.expense_type] = {'count': 0, 'amount': 0}
        type_statistics[report.expense_type]['count'] += 1
        type_statistics[report.expense_type]['amount'] += report.amount
    
    return jsonify({
        'month': month,
        'total_amount': round(total_amount, 2),
        'approved_amount': round(approved_amount, 2),
        'pending_amount': round(pending_amount, 2),
        'rejected_amount': round(rejected_amount, 2),
        'type_statistics': type_statistics
    }), 200