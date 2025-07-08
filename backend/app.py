from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import ipaddress

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///attendance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# 导入模型
from models import User, AttendanceRecord, LeaveRequest, ExpenseReport, WorkDiary, OutingReport, Schedule, SystemSettings

# 导入路由
from routes import auth, admin, attendance, leave, expense, diary, outing, schedule

# 注册蓝图
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(attendance.bp)
app.register_blueprint(leave.bp)
app.register_blueprint(expense.bp)
app.register_blueprint(diary.bp)
app.register_blueprint(outing.bp)
app.register_blueprint(schedule.bp)

@app.before_request
def load_logged_in_user():
    if request.endpoint and request.endpoint.startswith('auth'):
        return
    
    # 检查是否需要验证IP地址
    if request.endpoint in ['attendance.clock_in', 'attendance.clock_out']:
        if not verify_ip_address(request.remote_addr):
            return jsonify({'error': '只能在店内进行打卡操作'}), 403

def verify_ip_address(ip):
    """验证IP地址是否在允许范围内"""
    allowed_ips = SystemSettings.query.filter_by(key='allowed_ips').first()
    if not allowed_ips:
        return True  # 如果没有设置IP限制，则允许所有IP
    
    allowed_ip_list = allowed_ips.value.split(',')
    for allowed_ip in allowed_ip_list:
        try:
            if ipaddress.ip_address(ip) in ipaddress.ip_network(allowed_ip.strip(), strict=False):
                return True
        except ValueError:
            continue
    return False

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 创建默认管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@company.com',
                password=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("默认管理员用户创建成功: admin / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)