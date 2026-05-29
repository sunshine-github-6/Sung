from flask import Flask, jsonify, request, send_file
from config import Config
from datetime import datetime, timedelta
from models import db, OriginTracingBranches, OriginTracingLocations, OriginTracingMigrations, User, MigrationSubmission, PasswordResetRequest, UserBranchFavorite, SystemMeta
from flask_cors import CORS
import json
from sqlalchemy import text, func
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
import pandas as pd

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

try:
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/Library/Fonts/SimHei.ttf'
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
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
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
            
            try:
                db.session.execute(text('SELECT 1'))
                print("✅ 数据库连接: 成功")
            except Exception as e:
                print(f"❌ 数据库连接: 失败 - {str(e)}")
                return
            
            print("\n" + "-"*60)
            print("📈 数据统计")
            print("-"*60)
            
            branch_count = OriginTracingBranches.query.count()
            location_count = OriginTracingLocations.query.count()
            migration_count = OriginTracingMigrations.query.count()
            
            print(f"家族分支 (Branches):     {branch_count:>6} 条")
            print(f"地理地点 (Locations):     {location_count:>6} 条")
            print(f"迁徙记录 (Migrations):    {migration_count:>6} 条")
            
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
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176"], 
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
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

    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """通用文件上传接口"""
        try:
            if 'file' not in request.files:
                return jsonify({'status': 'error', 'message': '没有文件'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'status': 'error', 'message': '文件名为空'}), 400

            upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{file.filename}"
            filepath = os.path.join(upload_folder, filename)

            file.save(filepath)

            file_url = f"/api/uploads/{filename}"

            return jsonify({
                'status': 'success',
                'url': file_url,
                'filename': filename
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'上传失败: {str(e)}'}), 500

    @app.route('/api/upload/chunked', methods=['POST'])
    def upload_chunk():
        """分片文件上传接口"""
        try:
            if 'file' not in request.files:
                return jsonify({'status': 'error', 'message': '没有文件'}), 400

            file = request.files['file']
            file_id = request.form.get('fileId')
            chunk_index = int(request.form.get('chunkIndex', 0))
            total_chunks = int(request.form.get('totalChunks', 1))
            filename = request.form.get('fileName')

            if not file_id or not filename:
                return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400

            chunk_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'chunks', file_id)
            os.makedirs(chunk_folder, exist_ok=True)

            chunk_path = os.path.join(chunk_folder, f'chunk_{chunk_index}')
            file.save(chunk_path)

            return jsonify({
                'status': 'success',
                'chunkIndex': chunk_index,
                'totalChunks': total_chunks
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'分片上传失败: {str(e)}'}), 500

    @app.route('/api/upload/merge', methods=['POST'])
    def merge_chunks():
        """合并分片文件"""
        try:
            data = request.get_json()
            file_id = data.get('fileId')
            filename = data.get('fileName')
            total_chunks = int(data.get('totalChunks', 0))

            if not file_id or not filename:
                return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400

            chunk_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'chunks', file_id)

            if not os.path.exists(chunk_folder):
                return jsonify({'status': 'error', 'message': '分片文件不存在'}), 400

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            final_filename = f"{timestamp}_{filename}"
            upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            final_filepath = os.path.join(upload_folder, final_filename)

            with open(final_filepath, 'wb') as final_file:
                for i in range(total_chunks):
                    chunk_path = os.path.join(chunk_folder, f'chunk_{i}')
                    if os.path.exists(chunk_path):
                        with open(chunk_path, 'rb') as chunk_file:
                            final_file.write(chunk_file.read())
                        os.remove(chunk_path)

            import shutil
            shutil.rmtree(chunk_folder, ignore_errors=True)

            file_url = f"/api/uploads/{final_filename}"

            return jsonify({
                'status': 'success',
                'url': file_url,
                'filename': final_filename
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'合并失败: {str(e)}'}), 500

    @app.route('/api/uploads/<filename>')
    def serve_upload(filename):
        """提供上传文件的访问"""
        try:
            upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            filepath = os.path.join(upload_folder, filename)

            if os.path.exists(filepath):
                return send_file(filepath)
            else:
                return jsonify({'status': 'error', 'message': '文件不存在'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/statistics')
    def get_statistics():
        """获取统计数据"""
        try:
            branch_count = OriginTracingBranches.query.count()
            location_count = OriginTracingLocations.query.count()
            migration_count = OriginTracingMigrations.query.count()
            user_count = User.query.count()
            
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
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return jsonify({'status': 'error', 'message': '用户名已存在'}), 400
            
            user = User(
                username=username,
                real_name=real_name,
                phone=phone,
                role='user'
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
            user_id = request.args.get('user_id', 1, type=int)
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
            
            if not data.get('historical_name'):
                return jsonify({'status': 'error', 'message': '历史名称不能为空'}), 400
            
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
        try:
            migrations = OriginTracingMigrations.query.all()
            result = []
            for migration in migrations:
                result.append({
                    'id': migration.migration_id,
                    'branch_id': migration.branch_id,
                    'from_location_id': migration.from_location_id,
                    'to_location_id': migration.to_location_id,
                    'period': migration.migration_period,
                    'reason': migration.reason,
                    'key_figure': migration.key_figure
                })
            return jsonify({'status': 'success', 'data': result})
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取迁徙记录失败: {str(e)}'
            }), 500

    @app.route('/api/migrations', methods=['POST'])
    def create_migration():
        """创建新的迁徙记录"""
        try:
            data = request.get_json()

            if not data.get('branch_id'):
                return jsonify({'status': 'error', 'message': '所属分支不能为空'}), 400
            if not data.get('from_location_id'):
                return jsonify({'status': 'error', 'message': '迁出地不能为空'}), 400
            if not data.get('to_location_id'):
                return jsonify({'status': 'error', 'message': '迁入地不能为空'}), 400

            new_migration = OriginTracingMigrations(
                branch_id=data['branch_id'],
                from_location_id=data['from_location_id'],
                to_location_id=data['to_location_id'],
                migration_period=data.get('migration_period', ''),
                estimated_year=data.get('estimated_year'),
                reason=data.get('reason', ''),
                reason_detail=data.get('reason_detail', ''),
                key_figure=data.get('key_figure', ''),
                description=data.get('description', ''),
                route_points=data.get('route_points'),
                distance_km=data.get('distance_km')
            )

            db.session.add(new_migration)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': '迁徙记录创建成功',
                'data': {
                    'migration_id': new_migration.migration_id
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'创建迁徙记录失败: {str(e)}'
            }), 500

    @app.route('/api/migrations/<int:migration_id>', methods=['PUT'])
    def update_migration(migration_id):
        """更新迁徙记录"""
        try:
            migration = OriginTracingMigrations.query.get_or_404(migration_id)
            data = request.get_json()

            if 'branch_id' in data:
                migration.branch_id = data['branch_id']
            if 'from_location_id' in data:
                migration.from_location_id = data['from_location_id']
            if 'to_location_id' in data:
                migration.to_location_id = data['to_location_id']
            if 'migration_period' in data:
                migration.migration_period = data['migration_period']
            if 'estimated_year' in data:
                migration.estimated_year = data['estimated_year']
            if 'reason' in data:
                migration.reason = data['reason']
            if 'reason_detail' in data:
                migration.reason_detail = data['reason_detail']
            if 'key_figure' in data:
                migration.key_figure = data['key_figure']
            if 'description' in data:
                migration.description = data['description']
            if 'route_points' in data:
                migration.route_points = data['route_points']
            if 'distance_km' in data:
                migration.distance_km = data['distance_km']

            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': '迁徙记录更新成功'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'更新迁徙记录失败: {str(e)}'
            }), 500

    @app.route('/api/migrations/<int:migration_id>', methods=['DELETE'])
    def delete_migration(migration_id):
        """删除迁徙记录"""
        try:
            migration = OriginTracingMigrations.query.get_or_404(migration_id)
            db.session.delete(migration)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': '迁徙记录删除成功'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'删除迁徙记录失败: {str(e)}'
            }), 500

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

    @app.route('/api/password-reset/request', methods=['POST'])
    def request_password_reset():
        """用户申请密码重置"""
        try:
            data = request.get_json()
            username = data.get('username')
            reason = data.get('reason', '')

            if not username:
                return jsonify({
                    'status': 'error',
                    'message': '请输入用户名'
                }), 400

            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': '用户不存在'
                }), 404

            existing_request = PasswordResetRequest.query.filter_by(
                user_id=user.user_id,
                status='pending'
            ).first()

            if existing_request:
                return jsonify({
                    'status': 'error',
                    'message': '您已有一个待处理的密码重置请求，请耐心等待管理员处理'
                }), 400

            reset_request = PasswordResetRequest(
                user_id=user.user_id,
                reason=reason
            )

            db.session.add(reset_request)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': '密码重置申请已提交，请等待管理员处理',
                'data': {
                    'request_id': reset_request.request_id,
                    'requested_at': reset_request.requested_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'提交密码重置申请失败: {str(e)}'
            }), 500

    @app.route('/api/password-reset/status/<username>', methods=['GET'])
    def check_password_reset_status(username):
        """查询密码重置申请状态"""
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': '用户不存在'
                }), 404

            latest_request = PasswordResetRequest.query.filter_by(
                user_id=user.user_id
            ).order_by(PasswordResetRequest.requested_at.desc()).first()

            if not latest_request:
                return jsonify({
                    'status': 'success',
                    'data': {
                        'has_request': False
                    }
                })

            return jsonify({
                'status': 'success',
                'data': {
                    'has_request': True,
                    'request_id': latest_request.request_id,
                    'status': latest_request.status,
                    'reason': latest_request.reason,
                    'requested_at': latest_request.requested_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'reviewed_at': latest_request.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if latest_request.reviewed_at else None,
                    'review_comment': latest_request.review_comment
                }
            })

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'查询密码重置状态失败: {str(e)}'
            }), 500

    @app.route('/api/admin/password-reset-requests', methods=['GET'])
    def get_password_reset_requests():
        """获取所有密码重置请求（管理员）"""
        try:
            status = request.args.get('status', 'pending')
            
            query = PasswordResetRequest.query
            if status != 'all':
                query = query.filter_by(status=status)
            
            requests = query.order_by(PasswordResetRequest.requested_at.desc()).all()
            
            result = []
            for req in requests:
                result.append({
                    'request_id': req.request_id,
                    'user_id': req.user_id,
                    'username': req.user.username,
                    'real_name': req.user.real_name,
                    'reason': req.reason,
                    'status': req.status,
                    'requested_at': req.requested_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'reviewed_at': req.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if req.reviewed_at else None,
                    'review_comment': req.review_comment,
                    'reviewer_name': req.reviewer.real_name if req.reviewer else None
                })
            
            return jsonify({
                'status': 'success',
                'data': result
            })

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取密码重置请求列表失败: {str(e)}'
            }), 500

    @app.route('/api/admin/password-reset-requests/<int:request_id>/review', methods=['POST'])
    def review_password_reset_request(request_id):
        """审核密码重置请求（管理员）"""
        try:
            data = request.get_json()
            action = data.get('action')
            review_comment = data.get('review_comment', '')
            new_password = data.get('new_password', '123456')
            reviewer_id = data.get('reviewer_id')

            if action not in ['approve', 'reject']:
                return jsonify({
                    'status': 'error',
                    'message': '无效的操作类型'
                }), 400

            reset_request = PasswordResetRequest.query.get_or_404(request_id)
            
            if reset_request.status != 'pending':
                return jsonify({
                    'status': 'error',
                    'message': '该请求已被处理'
                }), 400

            reset_request.status = 'approved' if action == 'approve' else 'rejected'
            reset_request.review_comment = review_comment
            reset_request.reviewer_id = reviewer_id
            reset_request.reviewed_at = datetime.now()

            if action == 'approve':
                user = User.query.get(reset_request.user_id)
                user.set_password(new_password)
                reset_request.new_password = user.password_hash
                message = f'密码重置请求已批准，新密码为: {new_password}'
            else:
                message = '密码重置请求已拒绝'

            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': message
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'处理密码重置请求失败: {str(e)}'
            }), 500

    @app.route('/api/submissions/migration', methods=['POST'])
    def submit_migration_record():
        """用户提交迁徙口述史记录"""
        try:
            data = request.get_json()
            
            submission = MigrationSubmission(
                user_id=data['user_id'],
                submission_type='migration',
                branch_name=data['branch_name'],
                surname=data.get('surname', '姜'),
                content=data.get('migration_description') or data.get('content'),
                period=data.get('migration_period') or data.get('period'),
                estimated_year=data.get('estimated_year'),
                route_data=data.get('migration_route') or data.get('route_data'),
                reason=data.get('migration_reason') or data.get('reason'),
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
            
            submissions = MigrationSubmission.query.filter_by(user_id=user_id, submission_type='migration').all()
            result = []
            for submission in submissions:
                result.append({
                    'submission_id': submission.submission_id,
                    'branch_name': submission.branch_name,
                    'surname': submission.surname,
                    'migration_description': submission.content,
                    'content': submission.content,
                    'migration_period': submission.period,
                    'period': submission.period,
                    'estimated_year': submission.estimated_year,
                    'migration_route': submission.route_data,
                    'route_data': submission.route_data,
                    'migration_reason': submission.reason,
                    'reason': submission.reason,
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
            submissions = MigrationSubmission.query.filter_by(submission_type='migration').all()
            result = []
            for submission in submissions:
                result.append({
                    'submission_id': submission.submission_id,
                    'user_id': submission.user_id,
                    'branch_name': submission.branch_name,
                    'surname': submission.surname,
                    'migration_description': submission.content,
                    'content': submission.content,
                    'migration_period': submission.period,
                    'period': submission.period,
                    'estimated_year': submission.estimated_year,
                    'migration_route': submission.route_data,
                    'route_data': submission.route_data,
                    'migration_reason': submission.reason,
                    'reason': submission.reason,
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
            
            search_query = request.args.get('q', '').strip()
            
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
            
            if search_query:
                query = query.filter(
                    (OriginTracingBranches.branch_name.ilike(f'%{search_query}%')) |
                    (OriginTracingBranches.surname.ilike(f'%{search_query}%')) |
                    (OriginTracingBranches.ancestral_home.ilike(f'%{search_query}%')) |
                    (OriginTracingBranches.first_ancestor.ilike(f'%{search_query}%')) |
                    (OriginTracingBranches.historical_summary.ilike(f'%{search_query}%')) |
                    (OriginTracingMigrations.description.ilike(f'%{search_query}%')) |
                    (OriginTracingMigrations.key_figure.ilike(f'%{search_query}%')) |
                    (OriginTracingMigrations.reason.ilike(f'%{search_query}%')) |
                    (FromLocation.historical_name.ilike(f'%{search_query}%')) |
                    (FromLocation.modern_name.ilike(f'%{search_query}%')) |
                    (FromLocation.admin_region.ilike(f'%{search_query}%')) |
                    (ToLocation.historical_name.ilike(f'%{search_query}%')) |
                    (ToLocation.modern_name.ilike(f'%{search_query}%')) |
                    (ToLocation.admin_region.ilike(f'%{search_query}%'))
                )
            
            migrations = query.all()
            print(f"共查询到 {len(migrations)} 条迁徙记录")

            features = []
            coordinate_missing_count = 0
            
            for migration, branch, from_location, to_location in migrations:
                has_from_coords = from_location.longitude and from_location.latitude
                has_to_coords = to_location.longitude and to_location.latitude
                
                if has_from_coords and has_to_coords:
                    feature = {
                        'type': 'Feature',
                        'properties': {
                            'migration_id': migration.migration_id,
                            'branch_id': branch.branch_id,
                            'branch_name': branch.branch_name,
                            'surname': branch.surname or '姜',
                            'migration_period': migration.migration_period or '未知',
                            'estimated_year': migration.estimated_year,
                            'start_year': migration.estimated_year,
                            'end_year': migration.estimated_year,
                            'migration_reason': migration.reason or '',
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
                    coordinate_missing_count += 1
                    print(f"记录 {migration.migration_id} 缺少坐标信息，跳过")
            
            print(f"处理完成：有效记录 {len(features)} 条，缺少坐标 {coordinate_missing_count} 条")
            
            if not features and migrations:
                print("没有有效坐标的记录，返回所有记录（使用默认坐标）")
                for migration, branch, from_location, to_location in migrations:
                    from_lng = float(from_location.longitude) if from_location.longitude else 0
                    from_lat = float(from_location.latitude) if from_location.latitude else 0
                    to_lng = float(to_location.longitude) if to_location.longitude else 0
                    to_lat = float(to_location.latitude) if to_location.latitude else 0
                    
                    feature = {
                        'type': 'Feature',
                        'properties': {
                            'migration_id': migration.migration_id,
                            'branch_id': branch.branch_id,
                            'branch_name': branch.branch_name,
                            'surname': branch.surname or '姜',
                            'migration_period': migration.migration_period or '未知',
                            'estimated_year': migration.estimated_year,
                            'start_year': migration.estimated_year,
                            'end_year': migration.estimated_year,
                            'migration_reason': migration.reason or '',
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
            print(f"Error in get_migrations_geojson: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'type': 'FeatureCollection',
                'features': []
            })

    @app.route('/api/branches', methods=['POST'])
    def create_branch():
        """创建新的家族分支"""
        try:
            data = request.get_json()
            
            if not data.get('name'):
                return jsonify({'status': 'error', 'message': '分支名称不能为空'}), 400
            
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

    @app.route('/api/user/favorites', methods=['GET'])
    def get_user_favorites():
        """获取当前用户收藏的分支列表"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({
                    'status': 'error',
                    'message': '未提供认证信息'
                }), 401
            
            try:
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
                user_id = request.args.get('user_id')
                if not user_id:
                    return jsonify({
                        'status': 'error',
                        'message': '未提供用户ID'
                    }), 400
                user_id = int(user_id)
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': '认证信息无效'
                }), 401
            
            favorites = db.session.query(
                UserBranchFavorite,
                OriginTracingBranches
            ).join(
                OriginTracingBranches,
                UserBranchFavorite.branch_id == OriginTracingBranches.branch_id
            ).filter(
                UserBranchFavorite.user_id == user_id
            ).order_by(
                UserBranchFavorite.created_at.desc()
            ).all()
            
            result = []
            for favorite, branch in favorites:
                result.append({
                    'favorite_id': favorite.favorite_id,
                    'branch_id': branch.branch_id,
                    'branch_name': branch.branch_name,
                    'surname': branch.surname,
                    'ancestral_home': branch.ancestral_home,
                    'first_ancestor': branch.first_ancestor,
                    'created_at': favorite.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return jsonify({
                'status': 'success',
                'data': result
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取收藏列表失败: {str(e)}'
            }), 500

    @app.route('/api/user/favorites', methods=['POST'])
    def add_favorite():
        """添加分支到收藏"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            branch_id = data.get('branch_id')
            
            if not user_id or not branch_id:
                return jsonify({
                    'status': 'error',
                    'message': '缺少用户ID或分支ID'
                }), 400
            
            existing_favorite = UserBranchFavorite.query.filter_by(
                user_id=user_id,
                branch_id=branch_id
            ).first()
            
            if existing_favorite:
                return jsonify({
                    'status': 'error',
                    'message': '该分支已经在收藏列表中'
                }), 400
            
            new_favorite = UserBranchFavorite(
                user_id=user_id,
                branch_id=branch_id
            )
            
            db.session.add(new_favorite)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '添加收藏成功',
                'data': {
                    'favorite_id': new_favorite.favorite_id
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'添加收藏失败: {str(e)}'
            }), 500

    @app.route('/api/user/favorites/<int:favorite_id>', methods=['DELETE'])
    def remove_favorite(favorite_id):
        """从收藏中移除分支"""
        try:
            favorite = UserBranchFavorite.query.get_or_404(favorite_id)
            db.session.delete(favorite)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '移除收藏成功'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'移除收藏失败: {str(e)}'
            }), 500

    @app.route('/api/export/migration-report', methods=['GET'])
    def export_migration_report():
        """导出迁移分析报告PDF"""
        try:
            import io
            import pandas as pd
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.pdfgen import canvas
            from datetime import datetime

            import hashlib
            import sys
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

            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm

            FromLocation = aliased(OriginTracingLocations, name='from_location')
            ToLocation = aliased(OriginTracingLocations, name='to_location')
            
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
            ).all()
            
            migration_data = []
            for migration, branch, from_loc, to_loc in migrations:
                migration_data.append({
                    'branch': branch.branch_name,
                    'from_location': from_loc.historical_name,
                    'to_location': to_loc.historical_name,
                    'period': migration.migration_period,
                    'reason': migration.reason,
                    'key_figure': migration.key_figure
                })
            
            df = pd.DataFrame(migration_data)
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []

            title_style = ParagraphStyle('CustomTitle', fontName='Helvetica-Bold', fontSize=20, spaceAfter=20, textColor=colors.HexColor('#333333'))
            heading2_style = ParagraphStyle('CustomHeading2', fontName='Helvetica-Bold', fontSize=14, spaceAfter=12, textColor=colors.HexColor('#333333'))
            body_style = ParagraphStyle('CustomBody', fontName='Helvetica', fontSize=10, spaceAfter=8, textColor=colors.HexColor('#333333'))

            elements.append(Paragraph('姜姓迁徙分析报告', title_style))
            elements.append(Spacer(1, 20))

            elements.append(Paragraph('1. 迁徙概览', heading2_style))
            elements.append(Paragraph(f'总迁徙记录数: {len(migrations)}', body_style))
            elements.append(Spacer(1, 10))

            if len(migrations) == 0:
                elements.append(Paragraph('暂无迁徙数据', body_style))
            else:
                branch_counts = df['branch'].value_counts()
                reason_counts = df['reason'].value_counts()

                elements.append(Paragraph('2. 分支迁徙统计', heading2_style))
                branch_data = [[branch, str(count)] for branch, count in branch_counts.items()]
                if branch_data:
                    branch_table = Table([['分支', '迁徙次数']] + branch_data)
                    branch_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D3D3')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC'))
                    ]))
                    elements.append(branch_table)
                else:
                    elements.append(Paragraph('暂无分支数据', body_style))
                elements.append(Spacer(1, 20))

                elements.append(Paragraph('3. 迁徙原因分析', heading2_style))
                reason_data = [[reason, str(count)] for reason, count in reason_counts.items()]
                if reason_data:
                    reason_table = Table([['原因', '次数']] + reason_data)
                    reason_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D3D3')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC'))
                    ]))
                    elements.append(reason_table)
                else:
                    elements.append(Paragraph('暂无原因数据', body_style))
                elements.append(Spacer(1, 20))

                if not branch_counts.empty:
                    try:
                        branch_chart_buf = io.BytesIO()
                        plt.figure(figsize=(10, 6))
                        branch_counts.plot(kind='bar')
                        plt.xlabel('家族分支')
                        plt.ylabel('迁徙记录数量')
                        plt.title('各分支迁徙记录数量')
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        plt.savefig(branch_chart_buf, format='png')
                        plt.close()

                        img = Image(branch_chart_buf, width=18*cm, height=10*cm)
                        elements.append(Paragraph('4. 分支迁徙图表', heading2_style))
                        elements.append(img)
                        elements.append(Spacer(1, 20))
                    except Exception as chart_error:
                        print(f"Chart error: {chart_error}")
                        elements.append(Paragraph('4. 分支迁徙图表 (图表生成失败)', heading2_style))

            doc.build(elements)
            buffer.seek(0)

            return send_file(buffer, as_attachment=True, download_name=f'migration_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf', mimetype='application/pdf')
        except Exception as e:
            print(f"Export error: {e}")
            return jsonify({
                'status': 'error',
                'message': f'导出失败: {str(e)}'
            }), 500

    @app.route('/api/settings', methods=['GET'])
    def get_settings():
        """获取系统配置"""
        try:
            settings = {
                'general': {
                    'systemName': '姜姓迁徙溯源系统',
                    'systemVersion': '1.0.0',
                    'systemDescription': '用于记录和分析姜姓家族迁徙历史的系统',
                    'pageSize': 20,
                    'cacheTime': 30,
                    'maintenanceMode': False
                },
                'database': {
                    'host': Config.DB_HOST,
                    'port': int(Config.DB_PORT),
                    'database': Config.DB_NAME,
                    'username': Config.DB_USER,
                    'password': '',
                    'poolSize': 10,
                    'timeout': 30
                },
                'map': {
                    'amapKey': '',
                    'defaultLng': 108.0,
                    'defaultLat': 34.0,
                    'defaultZoom': 5,
                    'mapStyle': 'normal',
                    'enableHeatmap': True,
                    'heatmapRadius': 25
                },
                'security': {
                    'tokenExpireHours': 24,
                    'maxLoginAttempts': 5,
                    'passwordMinLength': 6,
                    'lockoutDuration': 30,
                    'enableCaptcha': False,
                    'enableCors': True,
                    'allowedOrigins': ['http://localhost:5173', 'http://localhost:5174']
                },
                'display': {
                    'primaryColor': '#409EFF',
                    'sidebarTheme': 'dark',
                    'headerTheme': 'light',
                    'pageSizeOptions': [10, 20, 50, 100],
                    'enableAnimation': True,
                    'showBreadcrumb': True
                }
            }
            
            return jsonify({
                'status': 'success',
                'data': settings
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取配置失败: {str(e)}'
            }), 500

    @app.route('/api/settings', methods=['PUT'])
    def update_settings():
        """更新系统配置"""
        try:
            data = request.get_json()
            config_type = data.get('type')
            config_data = data.get('data')
            
            if not config_type or not config_data:
                return jsonify({
                    'status': 'error',
                    'message': '配置类型和数据不能为空'
                }), 400
            
            return jsonify({
                'status': 'success',
                'message': f'{config_type}配置保存成功',
                'data': config_data
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'保存配置失败: {str(e)}'
            }), 500

    @app.route('/api/settings/test-database', methods=['POST'])
    def test_database_connection():
        """测试数据库连接"""
        try:
            data = request.get_json()
            host = data.get('host', 'localhost')
            port = data.get('port', 3306)
            database = data.get('database', 'Origin_Tracing')
            username = data.get('username', 'root')
            password = data.get('password', '')

            import pymysql
            from pymysql.constants import CLIENT

            connection = pymysql.connect(
                host=host,
                port=int(port),
                user=username,
                password=password,
                database=database,
                charset='utf8mb4',
                connect_timeout=10,
                client_flag=CLIENT.MULTI_STATEMENTS
            )

            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                result = cursor.fetchone()

            connection.close()

            return jsonify({
                'status': 'success',
                'message': '数据库连接测试成功'
            })
        except pymysql.err.OperationalError as e:
            return jsonify({
                'status': 'error',
                'message': f'数据库连接失败: {str(e)}'
            }), 500
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'数据库连接失败: {str(e)}'
            }), 500

    @app.route('/api/settings/backup', methods=['POST'])
    def create_backup():
        """创建数据库备份"""
        try:
            import subprocess
            from datetime import datetime
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_{timestamp}.sql'
            backup_path = os.path.join('backups', backup_filename)
            
            os.makedirs('backups', exist_ok=True)
            
            dump_cmd = [
                'mysqldump',
                '-h', Config.DB_HOST,
                '-P', str(Config.DB_PORT),
                '-u', Config.DB_USER,
                '-p' + Config.DB_PASSWORD,
                Config.DB_NAME
            ]
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                result = subprocess.run(dump_cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(backup_path)
                file_size_mb = round(file_size / (1024 * 1024), 2)
                
                return jsonify({
                    'status': 'success',
                    'message': '备份创建成功',
                    'data': {
                        'filename': backup_filename,
                        'size': f'{file_size_mb}MB',
                        'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'path': backup_path
                    }
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'备份失败: {result.stderr}'
                }), 500
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'创建备份失败: {str(e)}'
            }), 500

    @app.route('/api/settings/backups', methods=['GET'])
    def get_backups():
        """获取备份列表"""
        try:
            backups = []
            backup_dir = 'backups'
            
            if os.path.exists(backup_dir):
                for filename in os.listdir(backup_dir):
                    if filename.endswith('.sql'):
                        file_path = os.path.join(backup_dir, filename)
                        file_stat = os.stat(file_path)
                        file_size = round(file_stat.st_size / (1024 * 1024), 2)
                        created_at = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        
                        backups.append({
                            'filename': filename,
                            'size': f'{file_size}MB',
                            'createdAt': created_at
                        })
            
            backups.sort(key=lambda x: x['createdAt'], reverse=True)
            
            return jsonify({
                'status': 'success',
                'data': backups
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取备份列表失败: {str(e)}'
            }), 500

    @app.route('/api/settings/backup/<filename>', methods=['DELETE'])
    def delete_backup(filename):
        """删除备份文件"""
        try:
            backup_path = os.path.join('backups', filename)
            
            if os.path.exists(backup_path):
                os.remove(backup_path)
                return jsonify({
                    'status': 'success',
                    'message': '备份删除成功'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': '备份文件不存在'
                }), 404
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'删除备份失败: {str(e)}'
            }), 500

    @app.route('/api/settings/backup/<filename>', methods=['GET'])
    def download_backup(filename):
        """下载备份文件"""
        try:
            backup_path = os.path.join('backups', filename)
            
            if os.path.exists(backup_path):
                return send_file(
                    backup_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/sql'
                )
            else:
                return jsonify({
                    'status': 'error',
                    'message': '备份文件不存在'
                }), 404
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'下载备份失败: {str(e)}'
            }), 500

    @app.route('/api/settings/logs', methods=['GET'])
    def get_system_logs():
        """获取系统日志"""
        try:
            level = request.args.get('level', '')
            log_type = request.args.get('type', '')
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))

            logs = []
            total = 0

            return jsonify({
                'status': 'success',
                'data': {
                    'logs': logs,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取系统日志失败: {str(e)}'
            }), 500

    @app.route('/api/admin/reports/user-activity', methods=['GET'])
    def get_user_activity_report():
        """获取用户活跃度报表"""
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            query = User.query
            
            if start_date:
                query = query.filter(User.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                query = query.filter(User.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
            
            users = query.all()
            
            total_users = len(users)
            active_users = sum(1 for u in users if u.last_login and (datetime.now() - u.last_login).days <= 30)
            new_users_this_month = sum(1 for u in users if u.created_at and (datetime.now() - u.created_at).days <= 30)
            
            daily_stats = {}
            for user in users:
                if user.created_at:
                    date_key = user.created_at.strftime('%Y-%m-%d')
                    daily_stats[date_key] = daily_stats.get(date_key, 0) + 1
            
            return jsonify({
                'status': 'success',
                'data': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'new_users_this_month': new_users_this_month,
                    'daily_stats': daily_stats
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取用户活跃度报表失败: {str(e)}'
            }), 500

    @app.route('/api/admin/reports/data-growth', methods=['GET'])
    def get_data_growth_report():
        """获取数据增长报表"""
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            branch_query = OriginTracingBranches.query
            location_query = OriginTracingLocations.query
            migration_query = OriginTracingMigrations.query
            
            if start_date:
                branch_query = branch_query.filter(OriginTracingBranches.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
                location_query = location_query.filter(OriginTracingLocations.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
                migration_query = migration_query.filter(OriginTracingMigrations.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                branch_query = branch_query.filter(OriginTracingBranches.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
                location_query = location_query.filter(OriginTracingLocations.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
                migration_query = migration_query.filter(OriginTracingMigrations.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
            
            total_branches = branch_query.count()
            total_locations = location_query.count()
            total_migrations = migration_query.count()
            
            branches_over_time = {}
            for branch in branch_query.all():
                if branch.created_at:
                    date_key = branch.created_at.strftime('%Y-%m-%d')
                    branches_over_time[date_key] = branches_over_time.get(date_key, 0) + 1
            
            locations_over_time = {}
            for loc in location_query.all():
                if loc.created_at:
                    date_key = loc.created_at.strftime('%Y-%m-%d')
                    locations_over_time[date_key] = locations_over_time.get(date_key, 0) + 1
            
            migrations_over_time = {}
            for mig in migration_query.all():
                if mig.created_at:
                    date_key = mig.created_at.strftime('%Y-%m-%d')
                    migrations_over_time[date_key] = migrations_over_time.get(date_key, 0) + 1
            
            return jsonify({
                'status': 'success',
                'data': {
                    'total_branches': total_branches,
                    'total_locations': total_locations,
                    'total_migrations': total_migrations,
                    'branches_over_time': branches_over_time,
                    'locations_over_time': locations_over_time,
                    'migrations_over_time': migrations_over_time
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取数据增长报表失败: {str(e)}'
            }), 500

    @app.route('/api/admin/reports/review-workload', methods=['GET'])
    def get_review_workload_report():
        """获取审核工作量报表"""
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            query = MigrationSubmission.query
            
            if start_date:
                query = query.filter(MigrationSubmission.submitted_at >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                query = query.filter(MigrationSubmission.submitted_at <= datetime.strptime(end_date, '%Y-%m-%d'))
            
            submissions = query.all()
            
            total_submissions = len(submissions)
            pending_submissions = sum(1 for s in submissions if s.status == 'pending')
            approved_submissions = sum(1 for s in submissions if s.status == 'approved')
            rejected_submissions = sum(1 for s in submissions if s.status == 'rejected')
            
            daily_stats = {}
            for submission in submissions:
                if submission.submitted_at:
                    date_key = submission.submitted_at.strftime('%Y-%m-%d')
                    if date_key not in daily_stats:
                        daily_stats[date_key] = {'total': 0, 'pending': 0, 'approved': 0, 'rejected': 0}
                    daily_stats[date_key]['total'] += 1
                    daily_stats[date_key][submission.status] = daily_stats[date_key].get(submission.status, 0) + 1
            
            return jsonify({
                'status': 'success',
                'data': {
                    'total_submissions': total_submissions,
                    'pending_submissions': pending_submissions,
                    'approved_submissions': approved_submissions,
                    'rejected_submissions': rejected_submissions,
                    'daily_stats': daily_stats
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'获取审核工作量报表失败: {str(e)}'
            }), 500

    @app.route('/api/admin/reports/export', methods=['GET'])
    def export_report():
        """导出报表"""
        try:
            report_type = request.args.get('type', 'user-activity')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            output = io.StringIO()
            output.write(f"报表类型: {report_type}\n")
            output.write(f"开始日期: {start_date or '不限'}\n")
            output.write(f"结束日期: {end_date or '不限'}\n")
            output.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write("\n数据内容请参考对应的报表API\n")
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.read().encode('utf-8')),
                as_attachment=True,
                download_name=f'report_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                mimetype='text/plain'
            )
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'导出报表失败: {str(e)}'
            }), 500