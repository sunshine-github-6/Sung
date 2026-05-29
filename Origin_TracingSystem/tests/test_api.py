"""
API功能测试脚本
用于测试系统API接口功能
运行方式: python test_api.py
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User, OriginTracingBranches, OriginTracingLocations, OriginTracingMigrations


class TestAPI(unittest.TestCase):
    """API接口测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.app = create_app()
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['TESTING'] = True
        cls.app.config['SECRET_KEY'] = 'test-secret-key'

        with cls.app.app_context():
            db.create_all()

            admin = User(username='admin', role='admin', email='admin@test.com')
            admin.set_password('admin123')
            db.session.add(admin)

            branch = OriginTracingBranches(
                branch_name='测试分支',
                surname='姜',
                ancestral_home='测试地点'
            )
            db.session.add(branch)

            location1 = OriginTracingLocations(
                historical_name='测试地点A',
                longitude=116.4,
                latitude=39.9,
                location_type='origin'
            )
            location2 = OriginTracingLocations(
                historical_name='测试地点B',
                longitude=121.5,
                latitude=31.2,
                location_type='settlement'
            )
            db.session.add_all([location1, location2])
            db.session.commit()

            cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_api(self):
        """测试首页API"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

    def test_statistics_api(self):
        """测试统计API"""
        response = self.client.get('/api/statistics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)

    def test_branches_api(self):
        """测试分支列表API"""
        response = self.client.get('/api/branches')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)

    def test_locations_api(self):
        """测试地点列表API"""
        response = self.client.get('/api/locations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)

    def test_migrations_api(self):
        """测试迁徙记录API"""
        response = self.client.get('/api/migrations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_migrations_geojson_api(self):
        """测试GeoJSON格式迁徙数据API"""
        response = self.client.get('/api/migrations-geojson')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('type', data)
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertIn('features', data)

    def test_login_api_success(self):
        """测试登录API - 成功登录"""
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_login_api_failure(self):
        """测试登录API - 密码错误"""
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')

    def test_register_api(self):
        """测试注册API"""
        response = self.client.post('/api/auth/register', json={
            'username': 'newuser',
            'password': 'newpass123',
            'real_name': '新用户'
        })
        self.assertIn(response.status_code, [200, 201, 400])

    def test_create_branch_api(self):
        """测试创建分支API"""
        response = self.client.post('/api/branches', json={
            'name': '新测试分支',
            'surname': '姜',
            'ancestral_home': '新测试地点'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_create_location_api(self):
        """测试创建地点API"""
        response = self.client.post('/api/locations', json={
            'historical_name': '新测试地点C',
            'longitude': 120.0,
            'latitude': 30.0,
            'type': 'settlement'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_settings_api(self):
        """测试系统设置API"""
        response = self.client.get('/api/settings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)


class TestDatabaseOperations(unittest.TestCase):
    """数据库操作测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.app = create_app()
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['TESTING'] = True

        with cls.app.app_context():
            db.create_all()
            cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_db_connection(self):
        """测试数据库连接"""
        response = self.client.get('/api/test-db')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_crud_operations(self):
        """测试CRUD操作"""
        with self.app.app_context():
            branch = OriginTracingBranches(
                branch_name='CRUD测试分支',
                surname='姜'
            )
            db.session.add(branch)
            db.session.commit()

            saved_branch = OriginTracingBranches.query.filter_by(branch_name='CRUD测试分支').first()
            self.assertIsNotNone(saved_branch)

            saved_branch.ancestral_home = '更新后的地点'
            db.session.commit()

            updated_branch = OriginTracingBranches.query.filter_by(branch_name='CRUD测试分支').first()
            self.assertEqual(updated_branch.ancestral_home, '更新后的地点')

            db.session.delete(updated_branch)
            db.session.commit()

            deleted_branch = OriginTracingBranches.query.filter_by(branch_name='CRUD测试分支').first()
            self.assertIsNone(deleted_branch)


if __name__ == '__main__':
    print("=" * 60)
    print("祖籍溯源系统 - API功能测试")
    print("=" * 60)
    print()
    unittest.main(verbosity=2)
