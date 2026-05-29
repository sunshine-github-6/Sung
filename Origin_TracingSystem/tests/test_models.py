import unittest
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User, OriginTracingBranches, OriginTracingLocations, OriginTracingMigrations


class TestModels(unittest.TestCase):
    """测试数据模型"""

    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.app = create_app('testing')
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['TESTING'] = True
        cls.app.config['SECRET_KEY'] = 'test-secret-key'

        with cls.app.app_context():
            db.create_all()

            admin = User(username='admin', role='admin', email='admin@test.com')
            admin.set_password('admin123')
            db.session.add(admin)

            test_user = User(username='testuser', role='user', email='test@test.com')
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()

            cls.admin_id = admin.user_id
            cls.user_id = test_user.user_id

    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        """每个测试方法前执行"""
        self.client = self.app.test_client()

    def test_user_creation(self):
        """测试用户创建"""
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@test.com')
            self.assertEqual(user.role, 'user')

    def test_user_password_hashing(self):
        """测试用户密码哈希"""
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertTrue(user.check_password('test123'))
            self.assertFalse(user.check_password('wrongpassword'))

    def test_branch_creation(self):
        """测试家族分支创建"""
        with self.app.app_context():
            branch = OriginTracingBranches(
                branch_name='山东分支',
                surname='姜',
                ancestral_home='山东莱州',
                first_ancestor='姜子牙'
            )
            db.session.add(branch)
            db.session.commit()

            saved_branch = OriginTracingBranches.query.filter_by(branch_name='山东分支').first()
            self.assertIsNotNone(saved_branch)
            self.assertEqual(saved_branch.ancestral_home, '山东莱州')

    def test_location_creation(self):
        """测试地点创建"""
        with self.app.app_context():
            location = OriginTracingLocations(
                historical_name='莱州',
                modern_name='山东烟台莱州市',
                longitude=119.9423,
                latitude=37.1772,
                location_type='origin',
                admin_region='山东省烟台市'
            )
            db.session.add(location)
            db.session.commit()

            saved_location = OriginTracingLocations.query.filter_by(historical_name='莱州').first()
            self.assertIsNotNone(saved_location)
            self.assertEqual(saved_location.location_type, 'origin')

    def test_migration_creation(self):
        """测试迁徙记录创建"""
        with self.app.app_context():
            branch = OriginTracingBranches.query.first()
            from_loc = OriginTracingLocations(
                historical_name='莱州',
                longitude=119.9423,
                latitude=37.1772,
                location_type='origin'
            )
            to_loc = OriginTracingLocations(
                historical_name='江苏南京',
                longitude=118.7969,
                latitude=32.0603,
                location_type='settlement'
            )
            db.session.add(from_loc)
            db.session.add(to_loc)
            db.session.commit()

            migration = OriginTracingMigrations(
                branch_id=branch.branch_id,
                from_location_id=from_loc.location_id,
                to_location_id=to_loc.location_id,
                migration_period='明朝初期',
                estimated_year=1380,
                reason='战乱避祸',
                description='因战乱从莱州迁往南京'
            )
            db.session.add(migration)
            db.session.commit()

            saved_migration = OriginTracingMigrations.query.first()
            self.assertIsNotNone(saved_migration)
            self.assertEqual(saved_migration.estimated_year, 1380)


class TestDistanceCalculation(unittest.TestCase):
    """测试距离计算算法"""

    def haversine_distance(self, point1, point2):
        """Haversine公式计算两点间距离"""
        R = 6371
        lat1, lon1 = point1[1] * math.pi / 180, point1[0] * math.pi / 180
        lat2, lon2 = point2[1] * math.pi / 180, point2[0] * math.pi / 180

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def test_same_point_distance(self):
        """测试同一点距离为0"""
        point = (116.4, 39.9)
        distance = self.haversine_distance(point, point)
        self.assertAlmostEqual(distance, 0, places=5)

    def test_beijing_to_shanghai(self):
        """测试北京到上海距离（约1060公里）"""
        beijing = (116.4, 39.9)
        shanghai = (121.5, 31.2)
        distance = self.haversine_distance(beijing, shanghai)
        self.assertGreater(distance, 1000)
        self.assertLess(distance, 1200)

    def test_nearby_cities(self):
        """测试近距离城市"""
        beijing = (116.4, 39.9)
        tianjin = (117.2, 39.1)
        distance = self.haversine_distance(beijing, tianjin)
        self.assertGreater(distance, 50)
        self.assertLess(distance, 200)


class TestDirectionCalculation(unittest.TestCase):
    """测试方向计算算法"""

    def calculate_direction(self, start, end):
        """根据起止点计算方向"""
        deltaX = end[0] - start[0]
        deltaY = end[1] - start[1]
        angle = math.atan2(deltaY, deltaX) * 180 / math.pi

        if angle < 0:
            angle += 360

        if 337.5 <= angle or angle < 22.5:
            return '东'
        elif 22.5 <= angle < 67.5:
            return '东北'
        elif 67.5 <= angle < 112.5:
            return '北'
        elif 112.5 <= angle < 157.5:
            return '西北'
        elif 157.5 <= angle < 202.5:
            return '西'
        elif 202.5 <= angle < 247.5:
            return '西南'
        elif 247.5 <= angle < 292.5:
            return '南'
        else:
            return '东南'

    def test_east_direction(self):
        """测试向东方向"""
        start = (110.0, 30.0)
        end = (120.0, 30.0)
        direction = self.calculate_direction(start, end)
        self.assertEqual(direction, '东')

    def test_north_direction(self):
        """测试向北方向"""
        start = (110.0, 30.0)
        end = (110.0, 40.0)
        direction = self.calculate_direction(start, end)
        self.assertEqual(direction, '北')

    def test_northeast_direction(self):
        """测试向东北方向"""
        start = (110.0, 30.0)
        end = (115.0, 35.0)
        direction = self.calculate_direction(start, end)
        self.assertEqual(direction, '东北')


class TestRouteLength(unittest.TestCase):
    """测试路线长度计算"""

    def calculate_route_length(self, coordinates):
        """计算路线总长度"""
        def haversine_distance(p1, p2):
            R = 6371
            lat1, lon1 = p1[1] * math.pi / 180, p1[0] * math.pi / 180
            lat2, lon2 = p2[1] * math.pi / 180, p2[0] * math.pi / 180

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

            return R * c

        total = 0
        for i in range(1, len(coordinates)):
            total += haversine_distance(coordinates[i-1], coordinates[i])
        return total

    def test_single_segment(self):
        """测试单段路线"""
        route = [(116.4, 39.9), (121.5, 31.2)]
        length = self.calculate_route_length(route)
        self.assertGreater(length, 0)

    def test_multi_segment_route(self):
        """测试多段路线"""
        route = [
            (116.4, 39.9),
            (117.2, 39.1),
            (118.8, 32.0),
            (121.5, 31.2)
        ]
        length = self.calculate_route_length(route)
        self.assertGreater(length, 500)


if __name__ == '__main__':
    unittest.main()
