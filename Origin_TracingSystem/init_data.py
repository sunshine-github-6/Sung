"""
数据初始化脚本
用于初始化数据库的测试数据和演示数据
运行方式: python init_data.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, OriginTracingBranches, OriginTracingLocations, OriginTracingMigrations


def init_test_data():
    """初始化测试数据"""
    app = create_app('development')

    with app.app_context():
        db.create_all()

        print("=" * 50)
        print("开始初始化测试数据...")
        print("=" * 50)

        if User.query.filter_by(username='admin').first():
            print("数据已存在，跳过初始化")
            return

        print("\n[1/5] 创建用户数据...")
        admin = User(
            username='admin',
            role='admin',
            email='admin@example.com',
            real_name='系统管理员'
        )
        admin.set_password('admin123')

        test_user = User(
            username='testuser',
            role='user',
            email='test@example.com',
            real_name='测试用户'
        )
        test_user.set_password('test123')

        demo_user = User(
            username='demo',
            role='user',
            email='demo@example.com',
            real_name='演示用户'
        )
        demo_user.set_password('demo123')

        db.session.add_all([admin, test_user, demo_user])
        db.session.commit()
        print(f"  - 创建管理员用户: admin (ID: {admin.user_id})")
        print(f"  - 创建测试用户: testuser (ID: {test_user.user_id})")
        print(f"  - 创建演示用户: demo (ID: {demo_user.user_id})")

        print("\n[2/5] 创建家族分支数据...")
        branches = [
            OriginTracingBranches(
                branch_name='姜姓山东分支',
                surname='姜',
                ancestral_home='山东莱州',
                first_ancestor='姜子牙',
                historical_summary='姜姓起源于山东莱州，历经数千年繁衍，逐渐向全国扩散。该分支为姜姓主流分支之一。',
                source_reference='《姜姓族谱》'
            ),
            OriginTracingBranches(
                branch_name='姜姓陕西分支',
                surname='姜',
                ancestral_home='陕西宝鸡',
                first_ancestor='姜子牙',
                historical_summary='该分支从山东迁往陕西，是姜姓在西北地区的主要分布。',
                source_reference='《陕西姜姓族谱》'
            ),
            OriginTracingBranches(
                branch_name='姜姓江苏分支',
                surname='姜',
                ancestral_home='江苏南京',
                first_ancestor='姜子牙',
                historical_summary='该分支从山东迁往江苏，在江南地区繁衍生息。',
                source_reference='《江苏姜姓族谱》'
            ),
            OriginTracingBranches(
                branch_name='姜姓浙江分支',
                surname='姜',
                ancestral_home='浙江绍兴',
                first_ancestor='姜子牙',
                historical_summary='该分支从江苏迁往浙江，是姜姓在浙江地区的重要分支。',
                source_reference='《浙江姜姓族谱》'
            ),
            OriginTracingBranches(
                branch_name='姜姓安徽分支',
                surname='姜',
                ancestral_home='安徽合肥',
                first_ancestor='姜子牙',
                historical_summary='该分支从山东迁往安徽，在江淮地区发展壮大。',
                source_reference='《安徽姜姓族谱》'
            )
        ]
        db.session.add_all(branches)
        db.session.commit()
        for branch in branches:
            print(f"  - 创建分支: {branch.branch_name} (ID: {branch.branch_id})")

        print("\n[3/5] 创建地点数据...")
        locations = [
            OriginTracingLocations(
                historical_name='莱州',
                modern_name='山东烟台莱州市',
                longitude=119.9423,
                latitude=37.1772,
                location_type='origin',
                admin_region='山东省烟台市',
                description='姜姓发源地，古代称莱州，是姜子牙的封地'
            ),
            OriginTracingLocations(
                historical_name='营丘',
                modern_name='山东潍坊昌乐县',
                longitude=118.9580,
                latitude=36.7020,
                location_type='origin',
                admin_region='山东省潍坊市',
                description='姜姓早期居住地，与莱州相邻'
            ),
            OriginTracingLocations(
                historical_name='临淄',
                modern_name='山东淄博临淄区',
                longitude=118.2910,
                latitude=36.8230,
                location_type='settlement',
                admin_region='山东省淄博市',
                description='春秋时期齐国都城，姜姓在次地有重要发展'
            ),
            OriginTracingLocations(
                historical_name='咸阳',
                modern_name='陕西咸阳',
                longitude=108.7080,
                latitude=34.3290,
                location_type='settlement',
                admin_region='陕西省咸阳市',
                description='秦朝都城，姜姓贵族在此任职'
            ),
            OriginTracingLocations(
                historical_name='洛阳',
                modern_name='河南洛阳',
                longitude=112.4540,
                latitude=34.6190,
                location_type='settlement',
                admin_region='河南省洛阳市',
                description='东汉都城，姜姓在次地有较多分布'
            ),
            OriginTracingLocations(
                historical_name='南京',
                modern_name='江苏南京',
                longitude=118.7969,
                latitude=32.0603,
                location_type='settlement',
                admin_region='江苏省南京市',
                description='明朝初期姜姓大量迁入，逐渐成为重要聚居地'
            ),
            OriginTracingLocations(
                historical_name='苏州',
                modern_name='江苏苏州',
                longitude=120.5853,
                latitude=31.2989,
                location_type='settlement',
                admin_region='江苏省苏州市',
                description='江南鱼米之乡，姜姓在次地经商定居'
            ),
            OriginTracingLocations(
                historical_name='绍兴',
                modern_name='浙江绍兴',
                longitude=120.5800,
                latitude=30.0300,
                location_type='settlement',
                admin_region='浙江省绍兴市',
                description='浙江姜姓主要聚居地之一'
            ),
            OriginTracingLocations(
                historical_name='合肥',
                modern_name='安徽合肥',
                longitude=117.2830,
                latitude=31.8610,
                location_type='settlement',
                admin_region='安徽省合肥市',
                description='安徽姜姓发源地之一'
            ),
            OriginTracingLocations(
                historical_name='宝鸡',
                modern_name='陕西宝鸡',
                longitude=107.1449,
                latitude=34.3693,
                location_type='settlement',
                admin_region='陕西省宝鸡市',
                description='西北地区姜姓主要分布地'
            ),
            OriginTracingLocations(
                historical_name='开封',
                modern_name='河南开封',
                longitude=114.3410,
                latitude=34.7970,
                location_type='node',
                admin_region='河南省开封市',
                description='北宋都城，姜姓在次地有重要活动'
            ),
            OriginTracingLocations(
                historical_name='武昌',
                modern_name='湖北武汉',
                longitude=114.3110,
                latitude=30.5980,
                location_type='node',
                admin_region='湖北省武汉市',
                description='明清时期姜姓南迁的重要中转站'
            ),
            OriginTracingLocations(
                historical_name='南昌',
                modern_name='江西南昌',
                longitude=115.8580,
                latitude=28.6830,
                location_type='settlement',
                admin_region='江西省南昌市',
                description='江西姜姓主要聚居地'
            ),
            OriginTracingLocations(
                historical_name='福州',
                modern_name='福建福州',
                longitude=119.2960,
                latitude=26.0745,
                location_type='settlement',
                admin_region='福建省福州市',
                description='福建姜姓发源地之一'
            ),
            OriginTracingLocations(
                historical_name='广州',
                modern_name='广东广州',
                longitude=113.2640,
                latitude=23.1291,
                location_type='settlement',
                admin_region='广东省广州市',
                description='岭南地区姜姓主要分布地'
            )
        ]
        db.session.add_all(locations)
        db.session.commit()
        for loc in locations:
            print(f"  - 创建地点: {loc.historical_name} (ID: {loc.location_id}, 类型: {loc.location_type})")

        print("\n[4/5] 创建迁徙数据...")
        shandong_branch = OriginTracingBranches.query.filter_by(branch_name='姜姓山东分支').first()
        shanxi_branch = OriginTracingBranches.query.filter_by(branch_name='姜姓陕西分支').first()
        jiangsu_branch = OriginTracingBranches.query.filter_by(branch_name='姜姓江苏分支').first()
        zhejiang_branch = OriginTracingBranches.query.filter_by(branch_name='姜姓浙江分支').first()
        anhui_branch = OriginTracingBranches.query.filter_by(branch_name='姜姓安徽分支').first()

        laizhou = OriginTracingLocations.query.filter_by(historical_name='莱州').first()
        yingqiu = OriginTracingLocations.query.filter_by(historical_name='营丘').first()
        linzi = OriginTracingLocations.query.filter_by(historical_name='临淄').first()
        xianyang = OriginTracingLocations.query.filter_by(historical_name='咸阳').first()
        luoyang = OriginTracingLocations.query.filter_by(historical_name='洛阳').first()
        nanjing = OriginTracingLocations.query.filter_by(historical_name='南京').first()
        suzhou = OriginTracingLocations.query.filter_by(historical_name='苏州').first()
        shaoxing = OriginTracingLocations.query.filter_by(historical_name='绍兴').first()
        hefei = OriginTracingLocations.query.filter_by(historical_name='合肥').first()
        baoji = OriginTracingLocations.query.filter_by(historical_name='宝鸡').first()
        kaifeng = OriginTracingLocations.query.filter_by(historical_name='开封').first()
        wuchang = OriginTracingLocations.query.filter_by(historical_name='武昌').first()
        nanchang = OriginTracingLocations.query.filter_by(historical_name='南昌').first()
        fuzhou = OriginTracingLocations.query.filter_by(historical_name='福州').first()
        guangzhou = OriginTracingLocations.query.filter_by(historical_name='广州').first()

        migrations = [
            OriginTracingMigrations(
                branch_id=shandong_branch.branch_id,
                from_location_id=yingqiu.location_id,
                to_location_id=linzi.location_id,
                migration_period='西周初期',
                estimated_year=-1000,
                reason='封国就封',
                reason_detail='姜子牙被封为齐国国君，都城营丘，后迁都临淄',
                key_figure='姜子牙',
                description='姜子牙辅佐周文王建立周朝，后被封为齐国国君，建都临淄',
                route_points=[
                    [118.9580, 36.7020],
                    [118.2910, 36.8230]
                ]
            ),
            OriginTracingMigrations(
                branch_id=shandong_branch.branch_id,
                from_location_id=linzi.location_id,
                to_location_id=luoyang.location_id,
                migration_period='春秋战国',
                estimated_year=-500,
                reason='仕官迁居',
                reason_detail='姜姓贵族在洛阳任官，逐渐迁居',
                key_figure='姜小白',
                description='齐国公子姜小白后来成为齐桓公，在洛阳有活动',
                route_points=[
                    [118.2910, 36.8230],
                    [112.4540, 34.6190]
                ]
            ),
            OriginTracingMigrations(
                branch_id=shanxi_branch.branch_id,
                from_location_id=linzi.location_id,
                to_location_id=xianyang.location_id,
                migration_period='战国末期',
                estimated_year=-260,
                reason='战乱迁徙',
                reason_detail='因战国末期战乱，从山东迁往陕西',
                key_figure='姜姓贵族',
                description='齐国被秦所灭后，部分姜姓贵族迁往咸阳',
                route_points=[
                    [118.2910, 36.8230],
                    [108.7080, 34.3290]
                ]
            ),
            OriginTracingMigrations(
                branch_id=shanxi_branch.branch_id,
                from_location_id=xianyang.location_id,
                to_location_id=baoji.location_id,
                migration_period='秦汉时期',
                estimated_year=-200,
                reason='封地迁居',
                reason_detail='部分姜姓在宝鸡地区获得封地',
                key_figure='姜姓将领',
                description='秦朝将领姜姓后代在宝鸡地区定居',
                route_points=[
                    [108.7080, 34.3290],
                    [107.1449, 34.3693]
                ]
            ),
            OriginTracingMigrations(
                branch_id=jiangsu_branch.branch_id,
                from_location_id=luoyang.location_id,
                to_location_id=kaifeng.location_id,
                migration_period='东汉',
                estimated_year=50,
                reason='仕官迁居',
                reason_detail='东汉时期姜姓官员在开封任职',
                key_figure='姜姓士族',
                description='东汉时期，部分姜姓家族在开封地区发展',
                route_points=[
                    [112.4540, 34.6190],
                    [114.3410, 34.7970]
                ]
            ),
            OriginTracingMigrations(
                branch_id=jiangsu_branch.branch_id,
                from_location_id=kaifeng.location_id,
                to_location_id=nanjing.location_id,
                migration_period='明朝初期',
                estimated_year=1380,
                reason='战乱避祸',
                reason_detail='元末明初战乱，从开封迁往南京',
                key_figure='姜姓移民',
                description='元末明初战乱导致大量北方人南迁，姜姓也在此列',
                route_points=[
                    [114.3410, 34.7970],
                    [116.5000, 33.5000],
                    [118.7969, 32.0603]
                ]
            ),
            OriginTracingMigrations(
                branch_id=jiangsu_branch.branch_id,
                from_location_id=nanjing.location_id,
                to_location_id=suzhou.location_id,
                migration_period='明朝中后期',
                estimated_year=1550,
                reason='经商定居',
                reason_detail='南京姜姓商人到苏州经商，逐渐定居',
                key_figure='姜姓商人',
                description='明清时期，苏州商业繁荣，吸引姜姓商人迁入',
                route_points=[
                    [118.7969, 32.0603],
                    [120.5853, 31.2989]
                ]
            ),
            OriginTracingMigrations(
                branch_id=zhejiang_branch.branch_id,
                from_location_id=suzhou.location_id,
                to_location_id=shaoxing.location_id,
                migration_period='清朝',
                estimated_year=1720,
                reason='寻求发展',
                reason_detail='苏州姜姓分支迁往绍兴寻求更好发展',
                key_figure='姜姓商户',
                description='清代绍兴商业发达，姜姓从苏州迁入',
                route_points=[
                    [120.5853, 31.2989],
                    [120.5800, 30.0300]
                ]
            ),
            OriginTracingMigrations(
                branch_id=anhui_branch.branch_id,
                from_location_id=nanjing.location_id,
                to_location_id=hefei.location_id,
                migration_period='清朝中期',
                estimated_year=1780,
                reason='家族分支',
                reason_detail='南京姜姓分支迁往合肥',
                key_figure='姜氏家族',
                description='清代中期，合肥地区开发，吸引姜姓迁入',
                route_points=[
                    [118.7969, 32.0603],
                    [117.2830, 31.8610]
                ]
            ),
            OriginTracingMigrations(
                branch_id=jiangsu_branch.branch_id,
                from_location_id=wuchang.location_id,
                to_location_id=nanchang.location_id,
                migration_period='清朝末年',
                estimated_year=1860,
                reason='战乱迁徙',
                reason_detail='太平天国运动期间，从武昌迁往南昌',
                key_figure='姜姓难民',
                description='太平天国运动导致大量人口迁移，姜姓从湖北迁往江西',
                route_points=[
                    [114.3110, 30.5980],
                    [115.8580, 28.6830]
                ]
            ),
            OriginTracingMigrations(
                branch_id=jiangsu_branch.branch_id,
                from_location_id=nanchang.location_id,
                to_location_id=fuzhou.location_id,
                migration_period='民国时期',
                estimated_year=1930,
                reason='寻求发展',
                reason_detail='民国时期，部分江西姜姓迁往福建',
                key_figure='姜姓商人',
                description='民国时期福建沿海地区发展较快，吸引姜姓迁入',
                route_points=[
                    [115.8580, 28.6830],
                    [119.2960, 26.0745]
                ]
            ),
            OriginTracingMigrations(
                branch_id=jiangsu_branch.branch_id,
                from_location_id=fuzhou.location_id,
                to_location_id=guangzhou.location_id,
                migration_period='建国后',
                estimated_year=1960,
                reason='工作调动',
                reason_detail='建国后因工作调动从福州迁往广州',
                key_figure='姜姓干部',
                description='建国后支援广东建设，姜姓技术人员调往广州',
                route_points=[
                    [119.2960, 26.0745],
                    [113.2640, 23.1291]
                ]
            )
        ]

        for migration in migrations:
            coords = migration.route_points
            if len(coords) >= 2:
                def calc_distance(p1, p2):
                    import math
                    R = 6371
                    lat1, lon1 = p1[1] * math.pi / 180, p1[0] * math.pi / 180
                    lat2, lon2 = p2[1] * math.pi / 180, p2[0] * math.pi / 180
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    return R * c

                total = 0
                for i in range(1, len(coords)):
                    total += calc_distance(coords[i-1], coords[i])
                migration.distance_km = round(total, 2)

        db.session.add_all(migrations)
        db.session.commit()

        for mig in migrations:
            from_loc = OriginTracingLocations.query.get(mig.from_location_id)
            to_loc = OriginTracingLocations.query.get(mig.to_location_id)
            print(f"  - 创建迁徙: {from_loc.historical_name} → {to_loc.historical_name} ({mig.migration_period}, 约{mig.distance_km}公里)")

        print("\n[5/5] 数据初始化完成！")
        print("=" * 50)
        print("\n测试账号信息：")
        print("-" * 50)
        print("管理员账号: admin / admin123")
        print("测试账号: testuser / test123")
        print("演示账号: demo / demo123")
        print("-" * 50)
        print("\n共计创建：")
        print(f"  - 用户: 3个")
        print(f"  - 家族分支: {len(branches)}个")
        print(f"  - 地点: {len(locations)}个")
        print(f"  - 迁徙记录: {len(migrations)}条")
        print("=" * 50)


if __name__ == '__main__':
    init_test_data()
