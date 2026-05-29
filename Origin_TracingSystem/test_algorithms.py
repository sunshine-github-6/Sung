"""
算法测试脚本
用于测试系统中使用的关键算法
运行方式: python test_algorithms.py
"""

import math
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def haversine_distance(point1, point2):
    """
    使用Haversine公式计算两个地理坐标点之间的距离
    单位：公里
    """
    R = 6371

    lat1 = point1[1] * math.pi / 180
    lon1 = point1[0] * math.pi / 180
    lat2 = point2[1] * math.pi / 180
    lon2 = point2[0] * math.pi / 180

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def calculate_route_length(coordinates):
    """
    计算路线总长度
    coordinates: 坐标点列表，每个点为 [经度, 纬度]
    """
    total_distance = 0

    for i in range(1, len(coordinates)):
        total_distance += haversine_distance(coordinates[i-1], coordinates[i])

    return total_distance


def calculate_direction(start, end):
    """
    计算路线方向
    返回方向字符串（东、东北、北、西北、西、西南、南、东南）
    """
    deltaX = end[0] - start[0]
    deltaY = end[1] - start[1]

    angle = math.atan2(deltaY, deltaX) * 180 / math.pi

    if angle < 0:
        angle += 360

    if angle >= 337.5 or angle < 22.5:
        return '东'
    elif angle >= 22.5 and angle < 67.5:
        return '东北'
    elif angle >= 67.5 and angle < 112.5:
        return '北'
    elif angle >= 112.5 and angle < 157.5:
        return '西北'
    elif angle >= 157.5 and angle < 202.5:
        return '西'
    elif angle >= 202.5 and angle < 247.5:
        return '西南'
    elif angle >= 247.5 and angle < 292.5:
        return '南'
    elif angle >= 292.5 and angle < 337.5:
        return '东南'

    return '未知'


def create_curved_path(start, end):
    """
    创建平滑曲线路径
    使用贝塞尔曲线原理
    """
    midLng = (start[0] + end[0]) / 2
    midLat = (start[1] + end[1]) / 2

    distance = math.sqrt(
        math.pow(end[0] - start[0], 2) + math.pow(end[1] - start[1], 2)
    )

    curvature = min(distance * 0.3, 2)
    controlLng = midLng + (0.5 - 0.5) * curvature
    controlLat = midLat + curvature

    points = []
    segments = 20

    for i in range(segments + 1):
        t = i / segments
        lng = (1 - t)**2 * start[0] + 2 * (1 - t) * t * controlLng + t**2 * end[0]
        lat = (1 - t)**2 * start[1] + 2 * (1 - t) * t * controlLat + t**2 * end[1]
        points.append([lng, lat])

    return points


def generate_heatmap_data(migrations, locations):
    """
    生成热力图数据
    """
    data = []

    for migration in migrations:
        coords = migration.get('geometry', {}).get('coordinates', [])
        if not coords:
            continue

        if coords[0]:
            data.append({
                'lng': coords[0][0],
                'lat': coords[0][1],
                'weight': 3,
                'type': '起点'
            })

        if coords[-1]:
            data.append({
                'lng': coords[-1][0],
                'lat': coords[-1][1],
                'weight': 3,
                'type': '终点'
            })

        for i in range(1, len(coords) - 1):
            if coords[i]:
                data.append({
                    'lng': coords[i][0],
                    'lat': coords[i][1],
                    'weight': 2,
                    'type': '途径点'
                })

    for location in locations:
        lng = location.get('longitude')
        lat = location.get('latitude')
        loc_type = location.get('type', 'settlement')

        if lng and lat:
            weight = 5 if loc_type == 'origin' else 4 if loc_type == 'settlement' else 2
            data.append({
                'lng': float(lng),
                'lat': float(lat),
                'weight': weight,
                'type': loc_type
            })

    return data


def run_algorithm_tests():
    """运行算法测试"""
    print("=" * 60)
    print("迁徙路线系统 - 算法测试")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("1. 距离计算算法测试 (Haversine公式)")
    print("=" * 60)

    test_cases = [
        {
            'name': '北京到上海',
            'point1': [116.4, 39.9],
            'point2': [121.5, 31.2],
            'expected_range': (1000, 1200)
        },
        {
            'name': '北京到天津（近距离）',
            'point1': [116.4, 39.9],
            'point2': [117.2, 39.1],
            'expected_range': (50, 150)
        },
        {
            'name': '同一地点',
            'point1': [116.4, 39.9],
            'point2': [116.4, 39.9],
            'expected_range': (0, 0.1)
        },
        {
            'name': '山东莱州到江苏南京',
            'point1': [119.9423, 37.1772],
            'point2': [118.7969, 32.0603],
            'expected_range': (600, 800)
        },
        {
            'name': '山东到陕西（东西向长距离）',
            'point1': [118.2910, 36.8230],
            'point2': [108.7080, 34.3290],
            'expected_range': (900, 1100)
        }
    ]

    for i, test in enumerate(test_cases, 1):
        distance = haversine_distance(test['point1'], test['point2'])
        status = "✓" if test['expected_range'][0] <= distance <= test['expected_range'][1] else "✗"
        print(f"\n测试 {i}: {test['name']}")
        print(f"  起点: 经度{test['point1'][0]}, 纬度{test['point1'][1]}")
        print(f"  终点: 经度{test['point2'][0]}, 纬度{test['point2'][1]}")
        print(f"  计算距离: {distance:.2f} 公里")
        print(f"  预期范围: {test['expected_range'][0]}-{test['expected_range'][1]} 公里")
        print(f"  测试结果: {status}")

    print("\n" + "=" * 60)
    print("2. 路线长度计算算法测试")
    print("=" * 60)

    route_tests = [
        {
            'name': '单段路线（北京→上海）',
            'coordinates': [[116.4, 39.9], [121.5, 31.2]]
        },
        {
            'name': '两段路线（北京→天津→济南）',
            'coordinates': [
                [116.4, 39.9],
                [117.2, 39.1],
                [117.0, 36.6]
            ]
        },
        {
            'name': '多段路线（历史迁徙模拟）',
            'coordinates': [
                [118.9580, 36.7020],
                [118.2910, 36.8230],
                [112.4540, 34.6190],
                [114.3410, 34.7970],
                [118.7969, 32.0603]
            ]
        }
    ]

    for i, test in enumerate(route_tests, 1):
        length = calculate_route_length(test['coordinates'])
        print(f"\n测试 {i}: {test['name']}")
        print(f"  坐标点数量: {len(test['coordinates'])}")
        print(f"  路线总长度: {length:.2f} 公里")

        for j in range(len(test['coordinates']) - 1):
            seg_dist = haversine_distance(
                test['coordinates'][j],
                test['coordinates'][j + 1]
            )
            print(f"    段{j+1}: {seg_dist:.2f} 公里")

    print("\n" + "=" * 60)
    print("3. 方向计算算法测试")
    print("=" * 60)

    direction_tests = [
        {'name': '正东', 'start': [110.0, 30.0], 'end': [120.0, 30.0], 'expected': '东'},
        {'name': '正南', 'start': [110.0, 30.0], 'end': [110.0, 20.0], 'expected': '南'},
        {'name': '正西', 'start': [110.0, 30.0], 'end': [100.0, 30.0], 'expected': '西'},
        {'name': '正北', 'start': [110.0, 30.0], 'end': [110.0, 40.0], 'expected': '北'},
        {'name': '东北', 'start': [110.0, 30.0], 'end': [115.0, 35.0], 'expected': '东北'},
        {'name': '东南', 'start': [110.0, 30.0], 'end': [115.0, 25.0], 'expected': '东南'},
        {'name': '西南', 'start': [110.0, 30.0], 'end': [105.0, 25.0], 'expected': '西南'},
        {'name': '西北', 'start': [110.0, 30.0], 'end': [105.0, 35.0], 'expected': '西北'},
    ]

    for i, test in enumerate(direction_tests, 1):
        direction = calculate_direction(test['start'], test['end'])
        status = "✓" if direction == test['expected'] else "✗"
        print(f"\n测试 {i}: {test['name']}")
        print(f"  起点: {test['start']}")
        print(f"  终点: {test['end']}")
        print(f"  计算方向: {direction}")
        print(f"  预期方向: {test['expected']}")
        print(f"  测试结果: {status}")

    print("\n" + "=" * 60)
    print("4. 曲线路径生成算法测试")
    print("=" * 60)

    curved_test = {
        'name': '生成平滑曲线路径',
        'start': [116.4, 39.9],
        'end': [121.5, 31.2]
    }

    curved_path = create_curved_path(curved_test['start'], curved_test['end'])
    print(f"\n测试: {curved_test['name']}")
    print(f"  起点: {curved_test['start']}")
    print(f"  终点: {curved_test['end']}")
    print(f"  生成路径点数: {len(curved_path)}")
    print(f"  路径点示例（前5个）:")
    for i, point in enumerate(curved_path[:5], 1):
        print(f"    点{i}: [{point[0]:.4f}, {point[1]:.4f}]")

    print("\n" + "=" * 60)
    print("5. 热力图数据生成算法测试")
    print("=" * 60)

    sample_migrations = [
        {
            'geometry': {
                'coordinates': [
                    [119.9423, 37.1772],
                    [118.2910, 36.8230],
                    [118.7969, 32.0603]
                ]
            }
        },
        {
            'geometry': {
                'coordinates': [
                    [118.7969, 32.0603],
                    [120.5853, 31.2989]
                ]
            }
        }
    ]

    sample_locations = [
        {'longitude': 119.9423, 'latitude': 37.1772, 'type': 'origin'},
        {'longitude': 118.7969, 'latitude': 32.0603, 'type': 'settlement'},
        {'longitude': 120.5853, 'latitude': 31.2989, 'type': 'settlement'}
    ]

    heatmap_data = generate_heatmap_data(sample_migrations, sample_locations)
    print(f"\n生成的热点数据条目数: {len(heatmap_data)}")

    weight_stats = {}
    for item in heatmap_data:
        weight_stats[item['type']] = weight_stats.get(item['type'], 0) + 1

    print("\n按类型统计:")
    for loc_type, count in weight_stats.items():
        print(f"  {loc_type}: {count}个点")

    print("\n数据示例:")
    for i, item in enumerate(heatmap_data[:5], 1):
        print(f"  点{i}: 经度{item['lng']:.4f}, 纬度{item['lat']:.4f}, 权重{item['weight']}, 类型{item['type']}")

    print("\n" + "=" * 60)
    print("6. 综合测试 - 历史迁徙路线分析")
    print("=" * 60)

    historical_routes = [
        {
            'name': '姜姓从山东到江苏的迁徙',
            'period': '明朝初期',
            'coordinates': [
                [119.9423, 37.1772],
                [118.2910, 36.8230],
                [116.5000, 33.5000],
                [118.7969, 32.0603]
            ]
        },
        {
            'name': '姜姓从江苏到浙江的迁徙',
            'period': '清朝中期',
            'coordinates': [
                [118.7969, 32.0603],
                [120.5853, 31.2989],
                [120.5800, 30.0300]
            ]
        }
    ]

    for i, route in enumerate(historical_routes, 1):
        print(f"\n路线 {i}: {route['name']}")
        print(f"  时期: {route['period']}")
        print(f"  途经点数: {len(route['coordinates'])}")

        coords = route['coordinates']
        if len(coords) >= 2:
            start = coords[0]
            end = coords[-1]
            direction = calculate_direction(start, end)
            length = calculate_route_length(coords)

            print(f"  起点: 经度{start[0]:.4f}, 纬度{start[1]:.4f}")
            print(f"  终点: 经度{end[0]:.4f}, 纬度{end[1]:.4f}")
            print(f"  迁徙方向: {direction}")
            print(f"  总距离: {length:.2f} 公里")

            print(f"  分段详情:")
            for j in range(len(coords) - 1):
                seg_length = haversine_distance(coords[j], coords[j+1])
                seg_direction = calculate_direction(coords[j], coords[j+1])
                print(f"    段{j+1}: {seg_length:.2f}公里 ({seg_direction})")

    print("\n" + "=" * 60)
    print("所有算法测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    run_algorithm_tests()
