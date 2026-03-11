
from flask import Flask, jsonify, request, send_file
from config import Config
from datetime import datetime
from models import db, OriginTracingBranches, OriginTracingLocations, OriginTracingMigrations, User, MigrationSubmission
from flask_cors import CORS
import json
from sqlalchemy import text
from sqlalchemy.orm import aliased
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import io
import base64
import os

# 解决matplotlib中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题

# 解决reportlab中文显示问题
try:
    # 尝试注册中文字体
    # 这里使用系统默认的中文字体路径，根据实际情况调整
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',  # Windows系统
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # Linux系统
        '/Library/Fonts/SimHei.ttf'  # macOS系统
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('SimHei', font_path))
            break
except Exception as e:
    print(f"注册中文字体失败: {e}")

def print_database_info(app):
    """输出数据库连接信息和统计信息"""
    try:
        with app.app_context():
            # 获取数据库连接信息
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            # 隐藏密码
            if '@' in db_uri:
                parts = db_uri.split('@')
                if ':' in parts[0]:
                    user_pass = parts[0].split('://')[1]
                    if ':' in user_pass:
                        user = user_pass.split(':')[0]
                        db_uri_display = db_uri.replace(user_pass, f'{user}:***')
                    else:
                        db_uri_display = db_uri
                else:
                    db_uri_display = db_uri
            else:
                db_uri_display = db_uri
            
            print("\n" + "="*60)
            print("📊 数据库连接信息")
            print("="*60)
            print(f"数据库URI: {db_uri_display}")
            
            # 测试数据库连接
            try:
                db.session.execute(text('SELECT 1'))
                print("✅ 数据库连接: 成功")
            except Exception as e:
                print(f"❌ 数据库连接: 失败 - {str(e)}")
                return
            
            # 查询各表的数据条数
            print("\n" + "-"*60)
            print("📈 数据统计")
            print("-"*60)
            
            branch_count = OriginTracingBranches.query.count()
            location_count = OriginTracingLocations.query.count()
            migration_count = OriginTracingMigrations.query.count()
            
            print(f"家族分支 (Branches):     {branch_count:>6} 条")
            print(f"地理地点 (Locations):     {location_count:>6} 条")
            print(f"迁徙记录 (Migrations):    {migration_count:>6} 条")
            
            # 查询有效迁徙记录（有坐标的）
            try:
                FromLocation = aliased(OriginTracingLocations, name='from_location')
                ToLocation = aliased(OriginTracingLocations, name='to_location')
                
                valid_migrations = db.session.query(OriginTracingMigrations).join(
                    FromLocation, OriginTracingMigrations.from_location_id == FromLocation.location_id
                ).join(
                    ToLocation, OriginTracingMigrations.to_location_id == ToLocation.location_id
                ).filter(
                    FromLocation.longitude.isnot(None),
                    FromLocation.latitude.isnot(None),
                    ToLocation.longitude.isnot(None),
                    ToLocation.latitude.isnot(None)
                ).count()
                
                print(f"有效迁徙记录 (有坐标):   {valid_migrations:>6} 条")
            except Exception as e:
                print(f"⚠️  查询有效迁徙记录时出错: {str(e)}")
            
            # 查询有坐标的地点数量
            try:
                locations_with_coords = OriginTracingLocations.query.filter(
                    OriginTracingLocations.longitude.isnot(None),
                    OriginTracingLocations.latitude.isnot(None)
                ).count()
                print(f"有坐标的地点:           {locations_with_coords:>6} 条")
            except Exception as e:
                print(f"⚠️  查询有坐标地点时出错: {str(e)}")
            
            print("-"*60)
            print(f"总计:                    {branch_count + location_count + migration_count:>6} 条记录")
            print("="*60 + "\n")
            
    except Exception as e:
        print(f"\n❌ 获取数据库信息时出错: {str(e)}\n")
        import traceback
        traceback.print_exc()


def create_app():
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(Config)
    # 初始化数据库
    db.init_app(app)
    # 允许跨域请求
    CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176"], 
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    # 注册路由
    register_routes(app)
    return app


def register_routes(app):
    """注册路由"""
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/api/statistics')
    def get_statistics():
        """获取统计数据"""
        try:
            # 获取各个表的数据统计
            branch_count = OriginTracingBranches.query.count()
            location_count = OriginTracingLocations.query.count()
            migration_count = OriginTracingMigrations.query.count()
            user_count = User.query.count()
            
            # 获取有效的迁徙记录（有起止地点的）
            from sqlalchemy.orm import aliased
            FromLocation = aliased(OriginTracingLocations)
            ToLocation = aliased(OriginTracingLocations)
            
            valid_migrations = db.session.query(OriginTracingMigrations).join(
                FromLocation, OriginTracingMigrations.from_location_id == FromLocation.location_id
            ).join(
                ToLocation, OriginTracingMigrations.to_location_id == ToLocation.location_id
            ).filter(
                FromLocation.longitude.isnot(None),
                FromLocation.latitude.isnot(None),
                ToLocation.longitude.isnot(None),
                ToLocation.latitude.isnot(None)
            ).count()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'branches': branch_count,
                    'locations': location_count,
                    'migrations': migration_count,
                    'valid_migrations': valid_migrations,
                    'users': user_count
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取统计数据失败: {str(e)}'
            }), 500

    @app.route('/')
    def index():
        return jsonify({
            'message': '祖籍溯源系统API服务器',
            'endpoints': {
                'test_db': '/api/test-db',
                'branches': '/api/branches',
                'locations': '/api/locations',
                'migrations': '/api/migrations',
                'migrations_geojson': '/api/migrations-geojson'
            }
        })

    @app.route('/api')
    def api_index():
        return jsonify({
            'message': '祖籍溯源系统API',
            'port': {
                'test_db': '/api/test-db',
                'branches': '/api/branches',
                'locations': '/api/locations',
                'migrations': '/api/migrations',
                'migrations_geojson': '/api/migrations-geojson'
            }
        })

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """用户登录"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'status': 'error', 'message': '用户名和密码不能为空'}), 400
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                # 登录成功，生成token（简单实现，实际应用中应该使用JWT等）
                # 这里我们只是返回用户信息，前端存储在sessionStorage
                user.last_login = datetime.now()
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': '登录成功',
                    'data': {
                        'user_id': user.user_id,
                        'username': user.username,
                        'role': user.role,
                        'real_name': user.real_name,
                        'is_active': user.is_active
                    }
                })
            else:
                return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'登录失败: {str(e)}'
            }), 500

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """用户注册"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            real_name = data.get('real_name', '')
            phone = data.get('phone', '')
            
            if not username or not password:
                return jsonify({'status': 'error', 'message': '用户名和密码不能为空'}), 400
            
            # 检查用户名是否已存在
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return jsonify({'status': 'error', 'message': '用户名已存在'}), 400
            
            # 创建新用户
            user = User(
                username=username,
                real_name=real_name,
                phone=phone,
                role='user'  # 默认为普通用户
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '注册成功',
                'data': {
                    'user_id': user.user_id,
                    'username': user.username
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'注册失败: {str(e)}'
            }), 500

    @app.route('/api/auth/user-info', methods=['GET'])
    def get_user_info():
        """获取当前用户信息"""
        try:
            # 这里简化处理，实际应用中应该验证token
            # 为了简化，我们暂时返回默认用户信息
            user_id = request.args.get('user_id', 1, type=int)  # 默认获取第一个用户
            user = User.query.get_or_404(user_id)
            
            return jsonify({
                'status': 'success',
                'data': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'role': user.role,
                    'real_name': user.real_name,
                    'phone': user.phone,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取用户信息失败: {str(e)}'
            }), 500

    @app.route('/api/test-db')
    def test_db():
        """测试数据库连接"""
        try:
            # 测试查询
            branch_count = OriginTracingBranches.query.count()
            location_count = OriginTracingLocations.query.count()
            migration_count = OriginTracingMigrations.query.count()

            return jsonify({
                'status': 'success',
                'message': '数据库连接正常',
                'data': {
                    'branches': branch_count,
                    'locations': location_count,
                    'migrations': migration_count
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'数据库连接失败: {str(e)}'
            }), 500

    @app.route('/api/branches')
    def get_branches():
        """获取所有分支"""
        branches = OriginTracingBranches.query.all()
        result = []
        for branch in branches:
            result.append({
                'id': branch.branch_id,
                'name': branch.branch_name,
                'surname': branch.surname,
                'ancestral_home': branch.ancestral_home,
                'first_ancestor': branch.first_ancestor,
                'historical_summary': branch.historical_summary,
                'source_reference': branch.source_reference
            })
        return jsonify({'status': 'success', 'data': result})

    @app.route('/api/locations')
    def get_locations():
        """获取所有地点"""
        locations = OriginTracingLocations.query.all()
        result = []
        for location in locations:
            result.append({
                'id': location.location_id,
                'historical_name': location.historical_name,
                'modern_name': location.modern_name,
                'longitude': float(location.longitude) if location.longitude else None,
                'latitude': float(location.latitude) if location.latitude else None,
                'type': location.location_type,
                'region': location.admin_region
            })
        return jsonify({'status': 'success', 'data': result})

    @app.route('/api/locations', methods=['POST'])
    def create_location():
        """创建新的地点"""
        try:
            data = request.get_json()
            
            # 验证必要字段
            if not data.get('historical_name'):
                return jsonify({'status': 'error', 'message': '历史名称不能为空'}), 400
            
            # 创建新地点
            new_location = OriginTracingLocations(
                historical_name=data['historical_name'],
                modern_name=data.get('modern_name', ''),
                longitude=data.get('longitude'),
                latitude=data.get('latitude'),
                location_type=data.get('type', 'settlement'),
                admin_region=data.get('region', '')
            )
            
            db.session.add(new_location)
            db.session.commit()
            
            return jsonify({
                'status': 'success', 
                'message': '地点创建成功',
                'data': {
                    'id': new_location.location_id,
                    'historical_name': new_location.historical_name,
                    'modern_name': new_location.modern_name,
                    'longitude': float(new_location.longitude) if new_location.longitude else None,
                    'latitude': float(new_location.latitude) if new_location.latitude else None,
                    'type': new_location.location_type,
                    'region': new_location.admin_region
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'创建地点失败: {str(e)}'
            }), 500

    @app.route('/api/locations/<int:location_id>', methods=['PUT'])
    def update_location(location_id):
        """更新地点信息"""
        try:
            location = OriginTracingLocations.query.get_or_404(location_id)
            data = request.get_json()
            
            # 更新字段
            if 'historical_name' in data:
                location.historical_name = data['historical_name']
            if 'modern_name' in data:
                location.modern_name = data['modern_name']
            if 'longitude' in data:
                location.longitude = data['longitude']
            if 'latitude' in data:
                location.latitude = data['latitude']
            if 'type' in data:
                location.location_type = data['type']
            if 'region' in data:
                location.admin_region = data['region']
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '地点信息更新成功',
                'data': {
                    'id': location.location_id,
                    'historical_name': location.historical_name,
                    'modern_name': location.modern_name,
                    'longitude': float(location.longitude) if location.longitude else None,
                    'latitude': float(location.latitude) if location.latitude else None,
                    'type': location.location_type,
                    'region': location.admin_region
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'更新地点失败: {str(e)}'
            }), 500

    @app.route('/api/locations/<int:location_id>', methods=['DELETE'])
    def delete_location(location_id):
        """删除地点"""
        try:
            location = OriginTracingLocations.query.get_or_404(location_id)
            db.session.delete(location)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '地点删除成功'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'删除地点失败: {str(e)}'
            }), 500

    @app.route('/api/migrations')
    def get_migrations():
        """获取所有迁徙记录"""
        migrations = OriginTracingMigrations.query.all()
        result = []
        for migration in migrations:
            result.append({
                'id': migration.migration_id,
                'branch_id': migration.branch_id,
                'from_location_id': migration.from_location_id,
                'to_location_id': migration.to_location_id,
                'period': migration.migration_period,
                'reason': migration.migration_reason,
                'key_figure': migration.key_figure
            })
        return jsonify({'status': 'success', 'data': result})

    @app.route('/api/admin/users')
    def get_all_users():
        """获取所有用户信息（仅限管理员）"""
        try:
            users = User.query.all()
            result = []
            for user in users:
                result.append({
                    'user_id': user.user_id,
                    'username': user.username,
                    'role': user.role,
                    'real_name': user.real_name,
                    'phone': user.phone,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                })
            return jsonify({'status': 'success', 'data': result})
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取用户列表失败: {str(e)}'
            }), 500

    @app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        """更新用户信息（仅限管理员）"""
        try:
            user = User.query.get_or_404(user_id)
            data = request.get_json()
            
            # 更新允许的字段
            if 'role' in data:
                user.role = data['role']
            if 'real_name' in data:
                user.real_name = data['real_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': '用户信息更新成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'更新用户信息失败: {str(e)}'
            }), 500

    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        """删除用户（仅限管理员）"""
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return jsonify({'status': 'success', 'message': '用户删除成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'删除用户失败: {str(e)}'
            }), 500

    @app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
    def reset_user_password(user_id):
        """重置用户密码（仅限管理员）"""
        try:
            user = User.query.get_or_404(user_id)
            data = request.get_json()
            new_password = data.get('new_password', '123456')
            
            user.set_password(new_password)
            db.session.commit()
            return jsonify({'status': 'success', 'message': '密码重置成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'重置密码失败: {str(e)}'
            }), 500

    @app.route('/api/submissions/migration', methods=['POST'])
    def submit_migration_record():
        """用户提交迁徙口述史记录"""
        try:
            data = request.get_json()
            
            # 创建新的提交记录
            submission = MigrationSubmission(
                user_id=data['user_id'],
                branch_name=data['branch_name'],
                surname=data.get('surname', '姜'),
                migration_description=data['migration_description'],
                migration_period=data.get('migration_period'),
                estimated_year=data.get('estimated_year'),
                migration_route=data.get('migration_route'),
                migration_reason=data.get('migration_reason'),
                key_figures=data.get('key_figures'),
                source_reference=data.get('source_reference')
            )
            
            db.session.add(submission)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': '迁徙记录提交成功', 'data': {'submission_id': submission.submission_id}})
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'提交迁徙记录失败: {str(e)}'
            }), 500

    @app.route('/api/submissions/migration', methods=['GET'])
    def get_user_migration_submissions():
        """获取当前用户的迁徙口述史提交记录"""
        try:
            user_id = request.args.get('user_id', type=int)
            if not user_id:
                return jsonify({'status': 'error', 'message': '缺少用户ID参数'}), 400
            
            submissions = MigrationSubmission.query.filter_by(user_id=user_id).all()
            result = []
            for submission in submissions:
                result.append({
                    'submission_id': submission.submission_id,
                    'branch_name': submission.branch_name,
                    'surname': submission.surname,
                    'migration_description': submission.migration_description,
                    'migration_period': submission.migration_period,
                    'estimated_year': submission.estimated_year,
                    'migration_route': submission.migration_route,
                    'migration_reason': submission.migration_reason,
                    'key_figures': submission.key_figures,
                    'source_reference': submission.source_reference,
                    'status': submission.status,
                    'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                    'reviewed_at': submission.reviewed_at.isoformat() if submission.reviewed_at else None,
                    'review_comment': submission.review_comment
                })
            return jsonify({'status': 'success', 'data': result})
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取迁徙记录提交失败: {str(e)}'
            }), 500

    @app.route('/api/admin/submissions/migration', methods=['GET'])
    def get_all_migration_submissions():
        """获取所有迁徙口述史提交记录（管理员）"""
        try:
            submissions = MigrationSubmission.query.all()
            result = []
            for submission in submissions:
                result.append({
                    'submission_id': submission.submission_id,
                    'user_id': submission.user_id,
                    'branch_name': submission.branch_name,
                    'surname': submission.surname,
                    'migration_description': submission.migration_description,
                    'migration_period': submission.migration_period,
                    'estimated_year': submission.estimated_year,
                    'migration_route': submission.migration_route,
                    'migration_reason': submission.migration_reason,
                    'key_figures': submission.key_figures,
                    'source_reference': submission.source_reference,
                    'status': submission.status,
                    'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                    'reviewed_at': submission.reviewed_at.isoformat() if submission.reviewed_at else None,
                    'review_comment': submission.review_comment
                })
            return jsonify({'status': 'success', 'data': result})
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取迁徙记录提交失败: {str(e)}'
            }), 500

    @app.route('/api/admin/submissions/migration/<int:submission_id>', methods=['PUT'])
    def review_migration_submission(submission_id):
        """审核迁徙口述史提交记录（管理员）"""
        try:
            submission = MigrationSubmission.query.get_or_404(submission_id)
            data = request.get_json()
            
            # 更新审核状态和评论
            submission.status = data['status']
            submission.review_comment = data.get('review_comment', '')
            submission.reviewer_id = data.get('reviewer_id')
            submission.reviewed_at = datetime.now()
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': '审核操作成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'审核操作失败: {str(e)}'
            }), 500

    @app.route('/api/migrations-geojson')
    def get_migrations_geojson():
        """获取GeoJSON格式的迁徙数据"""
        try:
            FromLocation = aliased(OriginTracingLocations, name='from_location')
            ToLocation = aliased(OriginTracingLocations, name='to_location')
            
            # 获取搜索参数
            search_query = request.args.get('q', '').strip()
            
            # 构建查询
            query = db.session.query(
                OriginTracingMigrations,
                OriginTracingBranches,
                FromLocation,
                ToLocation
            ).join(
                OriginTracingBranches,
                OriginTracingMigrations.branch_id == OriginTracingBranches.branch_id
            ).join(
                FromLocation,
                OriginTracingMigrations.from_location_id == FromLocation.location_id
            ).join(
                ToLocation,
                OriginTracingMigrations.to_location_id == ToLocation.location_id
            )
            
            # 添加搜索条件
            if search_query:
                query = query.filter(
                    (OriginTracingBranches.branch_name.ilike(f'%{search_query}%')) |
                    (OriginTracingBranches.surname.ilike(f'%{search_query}%')) |
                    (OriginTracingBranches.ancestral_home.ilike(f'%{search_query}%')) |
                    (OriginTracingBranches.first_ancestor.ilike(f'%{search_query}%')) |
                    (OriginTracingBranches.historical_summary.ilike(f'%{search_query}%')) |
                    (OriginTracingMigrations.description.ilike(f'%{search_query}%')) |  # 修复：使用正确的字段名
                    (OriginTracingMigrations.key_figure.ilike(f'%{search_query}%')) |
                    (OriginTracingMigrations.migration_reason.ilike(f'%{search_query}%')) |
                    (FromLocation.historical_name.ilike(f'%{search_query}%')) |
                    (FromLocation.modern_name.ilike(f'%{search_query}%')) |
                    (FromLocation.admin_region.ilike(f'%{search_query}%')) |  # 新增：搜索行政区划
                    (ToLocation.historical_name.ilike(f'%{search_query}%')) |
                    (ToLocation.modern_name.ilike(f'%{search_query}%')) |
                    (ToLocation.admin_region.ilike(f'%{search_query}%'))  # 新增：搜索行政区划
                )
            
            # 执行查询
            migrations = query.all()
            print(f"共查询到 {len(migrations)} 条迁徙记录")

            features = []
            coordinate_missing_count = 0
            
            for migration, branch, from_location, to_location in migrations:
                # 检查坐标信息
                has_from_coords = from_location.longitude and from_location.latitude
                has_to_coords = to_location.longitude and to_location.latitude
                
                if has_from_coords and has_to_coords:
                    # 完整坐标的正常情况
                    feature = {
                        'type': 'Feature',
                        'properties': {
                            'migration_id': migration.migration_id,
                            'branch_name': branch.branch_name,
                            'surname': branch.surname or '姜',
                            'migration_period': migration.migration_period or '未知',
                            'estimated_year': migration.estimated_year,
                            'start_year': migration.estimated_year,  # 兼容性字段
                            'end_year': migration.estimated_year,    # 兼容性字段
                            'migration_reason': migration.migration_reason or '',
                            'key_figure': migration.key_figure or '',
                            'description': migration.description or '',
                            'from_name': from_location.historical_name,
                            'to_name': to_location.historical_name,
                            'historical_summary': branch.historical_summary or '',
                            'source_reference': branch.source_reference or ''
                        },
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': [
                                [float(from_location.longitude), float(from_location.latitude)],
                                [float(to_location.longitude), float(to_location.latitude)]
                            ]
                        }
                    }
                    features.append(feature)
                else:
                    # 缺少坐标的记录
                    coordinate_missing_count += 1
                    print(f"记录 {migration.migration_id} 缺少坐标信息，跳过")
            
            print(f"处理完成：有效记录 {len(features)} 条，缺少坐标 {coordinate_missing_count} 条")
            
            # 如果没有找到有效记录，返回所有记录（即使缺少坐标）
            if not features and migrations:
                print("没有有效坐标的记录，返回所有记录（使用默认坐标）")
                for migration, branch, from_location, to_location in migrations:
                    # 使用默认坐标 (0, 0) 代替
                    from_lng = float(from_location.longitude) if from_location.longitude else 0
                    from_lat = float(from_location.latitude) if from_location.latitude else 0
                    to_lng = float(to_location.longitude) if to_location.longitude else 0
                    to_lat = float(to_location.latitude) if to_location.latitude else 0
                    
                    feature = {
                        'type': 'Feature',
                        'properties': {
                            'migration_id': migration.migration_id,
                            'branch_name': branch.branch_name,
                            'surname': branch.surname or '姜',
                            'migration_period': migration.migration_period or '未知',
                            'estimated_year': migration.estimated_year,
                            'start_year': migration.estimated_year,  # 兼容性字段
                            'end_year': migration.estimated_year,    # 兼容性字段
                            'migration_reason': migration.migration_reason or '',
                            'key_figure': migration.key_figure or '',
                            'description': migration.description or '',
                            'from_name': from_location.historical_name,
                            'to_name': to_location.historical_name,
                            'historical_summary': branch.historical_summary or '',
                            'source_reference': branch.source_reference or '',
                            'warning': '该记录缺少部分坐标信息'
                        },
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': [
                                [from_lng, from_lat],
                                [to_lng, to_lat]
                            ]
                        }
                    }
                    features.append(feature)

            geojson = {
                'type': 'FeatureCollection',
                'features': features
            }
            
            return jsonify(geojson)
        except Exception as e:
            # 记录错误日志
            print(f"Error in get_migrations_geojson: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回空的GeoJSON而不是500错误
            return jsonify({
                'type': 'FeatureCollection',
                'features': []
            })

    @app.route('/api/branches', methods=['POST'])
    def create_branch():
        """创建新的家族分支"""
        try:
            data = request.get_json()
            
            # 验证必要字段
            if not data.get('name'):
                return jsonify({'status': 'error', 'message': '分支名称不能为空'}), 400
            
            # 创建新分支
            new_branch = OriginTracingBranches(
                branch_name=data['name'],
                surname=data.get('surname', '姜'),
                ancestral_home=data.get('ancestral_home', ''),
                first_ancestor=data.get('first_ancestor', ''),
                historical_summary=data.get('historical_summary', ''),
                source_reference=data.get('source_reference', '')
            )
            
            db.session.add(new_branch)
            db.session.commit()
            
            return jsonify({
                'status': 'success', 
                'message': '分支创建成功',
                'data': {
                    'id': new_branch.branch_id,
                    'name': new_branch.branch_name,
                    'surname': new_branch.surname,
                    'ancestral_home': new_branch.ancestral_home,
                    'first_ancestor': new_branch.first_ancestor,
                    'historical_summary': new_branch.historical_summary,
                    'source_reference': new_branch.source_reference
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'创建分支失败: {str(e)}'
            }), 500

    @app.route('/api/branches/<int:branch_id>', methods=['PUT'])
    def update_branch(branch_id):
        """更新家族分支信息"""
        try:
            branch = OriginTracingBranches.query.get_or_404(branch_id)
            data = request.get_json()
            
            # 更新字段
            if 'name' in data:
                branch.branch_name = data['name']
            if 'surname' in data:
                branch.surname = data['surname']
            if 'ancestral_home' in data:
                branch.ancestral_home = data['ancestral_home']
            if 'first_ancestor' in data:
                branch.first_ancestor = data['first_ancestor']
            if 'historical_summary' in data:
                branch.historical_summary = data['historical_summary']
            if 'source_reference' in data:
                branch.source_reference = data['source_reference']
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '分支信息更新成功',
                'data': {
                    'id': branch.branch_id,
                    'name': branch.branch_name,
                    'surname': branch.surname,
                    'ancestral_home': branch.ancestral_home,
                    'first_ancestor': branch.first_ancestor,
                    'historical_summary': branch.historical_summary,
                    'source_reference': branch.source_reference
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'更新分支失败: {str(e)}'
            }), 500

    @app.route('/api/branches/<int:branch_id>', methods=['DELETE'])
    def delete_branch(branch_id):
        """删除家族分支"""
        try:
            branch = OriginTracingBranches.query.get_or_404(branch_id)
            db.session.delete(branch)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '分支删除成功'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'删除分支失败: {str(e)}'
            }), 500

    @app.route('/api/export/migration-report', methods=['GET'])
    def export_migration_report():
        """导出迁移分析报告PDF"""
        try:
            # 收集迁移分析数据
            FromLocation = aliased(OriginTracingLocations, name='from_location')
            ToLocation = aliased(OriginTracingLocations, name='to_location')
            
            # 获取所有有效迁徙记录
            migrations = db.session.query(
                OriginTracingMigrations,
                OriginTracingBranches,
                FromLocation,
                ToLocation
            ).join(
                OriginTracingBranches,
                OriginTracingMigrations.branch_id == OriginTracingBranches.branch_id
            ).join(
                FromLocation,
                OriginTracingMigrations.from_location_id == FromLocation.location_id
            ).join(
                ToLocation,
                OriginTracingMigrations.to_location_id == ToLocation.location_id
            ).filter(
                FromLocation.longitude.isnot(None),
                FromLocation.latitude.isnot(None),
                ToLocation.longitude.isnot(None),
                ToLocation.latitude.isnot(None)
            ).all()
            
            # 统计数据
            total_migrations = len(migrations)
            branches = set()
            locations = set()
            migration_reasons = {}
            
            for migration, branch, from_loc, to_loc in migrations:
                branches.add(branch.branch_name)
                locations.add(from_loc.historical_name)
                locations.add(to_loc.historical_name)
                if migration.migration_reason:
                    reason = migration.migration_reason
                    migration_reasons[reason] = migration_reasons.get(reason, 0) + 1
            
            # 生成图表
            # 1. 迁徙原因分布饼图
            pie_chart_buf = io.BytesIO()
            if migration_reasons:
                labels = list(migration_reasons.keys())
                sizes = list(migration_reasons.values())
                plt.figure(figsize=(8, 6))
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title('迁徙原因分布')
                plt.tight_layout()
                plt.savefig(pie_chart_buf, format='png')
                plt.close()
            
            # 2. 迁徙记录数量柱状图（按分支）
            branch_migrations = {}
            for migration, branch, _, _ in migrations:
                branch_migrations[branch.branch_name] = branch_migrations.get(branch.branch_name, 0) + 1
            
            bar_chart_buf = io.BytesIO()
            if branch_migrations:
                labels = list(branch_migrations.keys())
                values = list(branch_migrations.values())
                plt.figure(figsize=(10, 6))
                plt.bar(labels, values)
                plt.xlabel('家族分支')
                plt.ylabel('迁徙记录数量')
                plt.title('各分支迁徙记录数量')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig(bar_chart_buf, format='png')
                plt.close()
            
            import hashlib
            import sys
            import os
            original_md5 = hashlib.md5
            def patched_md5(*args, **kwargs):
                kwargs.pop('usedforsecurity', None)
                return original_md5(*args, **kwargs)
            hashlib.md5 = patched_md5
            if hasattr(hashlib, 'openssl_md5'):
                original_openssl_md5 = hashlib.openssl_md5
                def patched_openssl_md5(*args, **kwargs):
                    kwargs.pop('usedforsecurity', None)
                    return original_openssl_md5(*args, **kwargs)
                hashlib.openssl_md5 = patched_openssl_md5
            for module in list(sys.modules.keys()):
                if module.startswith('reportlab'):
                    del sys.modules[module]
            
            # 现在导入reportlab模块
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # 注册中文字体
            try:
                font_paths = [
                    'C:/Windows/Fonts/simhei.ttf',  # Windows
                    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # Linux
                    '/Library/Fonts/SimHei.ttf'  # macOS
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('SimHei', font_path))
                        print(f"成功注册中文字体: {font_path}")
                        break
            except Exception as e:
                print(f"注册中文字体失败: {e}")
            
            # 创建PDF文档
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            
            # 添加标题
            styles = getSampleStyleSheet()
            
            # 创建支持中文的标题样式
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=20,
                alignment=1,  # 居中
                fontName='SimHei' if 'SimHei' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            
            # 创建支持中文的正文样式
            analysis_content_style = ParagraphStyle(
                'CustomAnalysisContent',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=10,
                leading=18,
                fontName='SimHei' if 'SimHei' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            
            # 创建支持中文的副标题样式
            summary_style = ParagraphStyle(
                'CustomSummary',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=15,
                fontName='SimHei' if 'SimHei' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            
            # 创建支持中文的小标题样式
            conclusion_style = ParagraphStyle(
                'CustomConclusion',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=10,
                fontName='SimHei' if 'SimHei' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            
            # 创建日期样式
            date_style = ParagraphStyle(
                'CustomDate',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20,
                alignment=2,  # 右对齐
                fontName='SimHei' if 'SimHei' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            
            # 第一部分：全中文内容
            elements.append(Paragraph('迁徙分析报告', title_style))
            elements.append(Paragraph(f'报告日期: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', date_style))
            elements.append(Spacer(1, 20))
            
            # 统计摘要（中文）
            elements.append(Paragraph('统计摘要', summary_style))
            
            # 统计数据表格（中文）
            data = [
                ['项目', '数值'],
                ['总迁徙记录数', str(total_migrations)],
                ['涉及家族分支数', str(len(branches))],
                ['涉及地点数', str(len(locations))]
            ]
            
            table = Table(data, colWidths=[8*cm, 6*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'SimHei' if 'SimHei' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # 迁徙原因分布图表（中文）
            elements.append(Paragraph('迁徙原因分布', summary_style))
            if migration_reasons:
                pie_chart_buf.seek(0)
                elements.append(Image(pie_chart_buf, width=14*cm, height=9*cm))
            else:
                elements.append(Paragraph('暂无迁徙原因数据', analysis_content_style))
            elements.append(Spacer(1, 20))
            
            # 分支迁徙记录数量图表（中文）
            elements.append(Paragraph('各分支迁徙记录数量', summary_style))
            if branch_migrations:
                bar_chart_buf.seek(0)
                elements.append(Image(bar_chart_buf, width=14*cm, height=9*cm))
            else:
                elements.append(Paragraph('暂无分支迁徙数据', analysis_content_style))
            elements.append(Spacer(1, 20))
            
            # 分析与结论（中文）
            elements.append(Paragraph('分析与结论', summary_style))
            
            # 分析内容1：迁徙趋势分析（中文）
            elements.append(Paragraph('1. 迁徙趋势分析', conclusion_style))
            elements.append(Paragraph('根据数据统计，共收集到 {} 条有效迁徙记录，涉及 {} 个家族分支和 {} 个地理地点。从时间分布来看，迁徙活动呈现出明显的阶段性特征，反映了不同历史时期的社会变迁。'.format(total_migrations, len(branches), len(locations)), analysis_content_style))
            elements.append(Spacer(1, 10))
            
            # 分析内容2：迁徙原因分析（中文）
            elements.append(Paragraph('2. 迁徙原因分析', conclusion_style))
            if migration_reasons:
                elements.append(Paragraph('迁徙原因主要包括经济因素、政治因素、自然环境因素等。从图表中可以看出，经济因素是最主要的迁徙驱动因素，占比最高。', analysis_content_style))
            else:
                elements.append(Paragraph('暂无足够的迁徙原因数据进行分析。', analysis_content_style))
            elements.append(Spacer(1, 10))
            
            # 分析内容3：地域分布分析（中文）
            elements.append(Paragraph('3. 地域分布分析', conclusion_style))
            elements.append(Paragraph('迁徙活动主要集中在中原地区与南方地区之间，反映了历史上人口南迁的大趋势。这种地域流动对于文化交流和民族融合起到了重要作用。', analysis_content_style))
            elements.append(Spacer(1, 10))
            
            # 结论（中文）
            elements.append(Paragraph('结论', conclusion_style))
            elements.append(Paragraph('1. 迁徙活动是人类历史发展的重要组成部分，反映了社会、经济、政治等多方面的变迁。', analysis_content_style))
            elements.append(Paragraph('2. 家族迁徙记录对于研究人口流动、文化传播和地域开发具有重要价值。', analysis_content_style))
            elements.append(Paragraph('3. 通过对迁徙数据的分析，可以更好地理解历史上的人口流动规律和文化演变过程。', analysis_content_style))
            elements.append(Spacer(1, 20))
            
            # 建议（中文）
            elements.append(Paragraph('建议', conclusion_style))
            elements.append(Paragraph('1. 继续收集和整理更多的迁徙记录，丰富数据库内容。', analysis_content_style))
            elements.append(Paragraph('2. 结合历史文献和考古资料，深入研究迁徙的历史背景和影响。', analysis_content_style))
            elements.append(Paragraph('3. 利用现代技术手段，如地理信息系统，更直观地展示迁徙路径和分布。', analysis_content_style))
            
            # 添加分页符
            from reportlab.platypus import PageBreak
            elements.append(PageBreak())
            
            # 第二部分：全英文内容
            elements.append(Paragraph('Migration Analysis Report', title_style))
            elements.append(Paragraph(f'Report Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', date_style))
            elements.append(Spacer(1, 20))
            
            # 统计摘要（英文）
            elements.append(Paragraph('Statistics Summary', summary_style))
            
            # 统计数据表格（英文）
            data_en = [
                ['Item', 'Value'],
                ['Total Migrations', str(total_migrations)],
                ['Involved Branches', str(len(branches))],
                ['Involved Locations', str(len(locations))]
            ]
            
            table_en = Table(data_en, colWidths=[8*cm, 6*cm])
            table_en.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table_en)
            elements.append(Spacer(1, 20))
            
            # 迁徙原因分布图表（英文）
            elements.append(Paragraph('Migration Reasons Distribution', summary_style))
            if migration_reasons:
                pie_chart_buf.seek(0)
                elements.append(Image(pie_chart_buf, width=14*cm, height=9*cm))
            else:
                elements.append(Paragraph('No migration reasons data', analysis_content_style))
            elements.append(Spacer(1, 20))
            
            # 分支迁徙记录数量图表（英文）
            elements.append(Paragraph('Migration Count by Branch', summary_style))
            if branch_migrations:
                bar_chart_buf.seek(0)
                elements.append(Image(bar_chart_buf, width=14*cm, height=9*cm))
            else:
                elements.append(Paragraph('No branch migration data', analysis_content_style))
            elements.append(Spacer(1, 20))
            
            # 分析与结论（英文）
            elements.append(Paragraph('Analysis and Conclusion', summary_style))
            
            # 分析内容1：迁徙趋势分析（英文）
            elements.append(Paragraph('1. Migration Trend Analysis', conclusion_style))
            elements.append(Paragraph('Based on the data statistics, we have collected {} valid migration records, involving {} family branches and {} geographical locations. From the time distribution perspective, migration activities show obvious periodic characteristics, reflecting social changes in different historical periods.'.format(total_migrations, len(branches), len(locations)), analysis_content_style))
            elements.append(Spacer(1, 10))
            
            # 分析内容2：迁徙原因分析（英文）
            elements.append(Paragraph('2. Migration Reason Analysis', conclusion_style))
            if migration_reasons:
                elements.append(Paragraph('Migration reasons mainly include economic factors, political factors, natural environment factors, etc. From the chart, it can be seen that economic factors are the most important driving factors for migration, accounting for the highest proportion.', analysis_content_style))
            else:
                elements.append(Paragraph('Insufficient migration reason data for analysis.', analysis_content_style))
            elements.append(Spacer(1, 10))
            
            # 分析内容3：地域分布分析（英文）
            elements.append(Paragraph('3. Geographical Distribution Analysis', conclusion_style))
            elements.append(Paragraph('Migration activities are mainly concentrated between the Central Plains region and the southern region, reflecting the historical trend of population南迁. This geographical flow has played an important role in cultural exchange and ethnic integration.', analysis_content_style))
            elements.append(Spacer(1, 10))
            
            # 结论（英文）
            elements.append(Paragraph('Conclusion', conclusion_style))
            elements.append(Paragraph('1. Migration activities are an important part of human history development, reflecting changes in social, economic, political and other aspects.', analysis_content_style))
            elements.append(Paragraph('2. Family migration records are of great value for studying population flow, cultural spread and regional development.', analysis_content_style))
            elements.append(Paragraph('3. Through the analysis of migration data, we can better understand the historical population flow patterns and cultural evolution processes.', analysis_content_style))
            elements.append(Spacer(1, 20))
            
            # 建议（英文）
            elements.append(Paragraph('Recommendations', conclusion_style))
            elements.append(Paragraph('1. Continue to collect and organize more migration records to enrich the database content.', analysis_content_style))
            elements.append(Paragraph('2. Combine historical documents and archaeological materials to deeply study the historical background and impact of migration.', analysis_content_style))
            elements.append(Paragraph('3. Use modern technical means, such as geographic information systems, to more intuitively display migration paths and distributions.', analysis_content_style))
            
            # 构建PDF
            doc.build(elements)
            
            # 重置缓冲区位置
            buffer.seek(0)
            
            # 返回PDF文件
            from flask import send_file
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f'migration_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                mimetype='application/pdf'
            )
            
        except Exception as e:
            print(f"导出PDF失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': f'导出PDF失败: {str(e)}'
            }), 500




if __name__ == '__main__':
    app = create_app()
    # 输出数据库信息
    print_database_info(app)
    print("🚀 服务器启动中...")
    app.run(debug=True, port=5000)