import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
from scipy.optimize import differential_evolution
import matplotlib.pyplot as plt

# 加载数据集
intersection_file_path = 'B4_intersections_unique_valid.csv'
intersection_data = pd.read_csv(intersection_file_path, header=None, names=["IntersectionID", "Coordinates"])

# 处理 Coordinates 列
intersection_data['Coordinates'] = intersection_data['Coordinates'].str.replace('LINESTRING\\(', '', regex=True).str.replace('\\)', '', regex=True)

# 定义一个函数，将坐标分割为单独的经度和纬度列表
def split_coordinates(coord_string):
    latitudes = []
    longitudes = []
    for coord in coord_string.split(','):
        try:
            lon, lat = map(float, coord.split())
            latitudes.append(lat)
            longitudes.append(lon)
        except ValueError:
            continue
    return latitudes, longitudes

# 应用函数以拆分坐标
intersection_data['Latitude'], intersection_data['Longitude'] = zip(*intersection_data['Coordinates'].apply(split_coordinates))

# 移除空的列表
intersection_data = intersection_data[intersection_data['Latitude'].map(len) > 0]

# 设置权重和损失函数
weights = {'w1': 0.3, 'w2': 0.3, 'w3': 0.4}

# 评估曲线质量
def evaluate_curve_quality(points):
    path_length = 0
    curvature_radius = 0

    # 计算路径长度
    for i in range(1, len(points)):
        prev_point = points[i-1]
        curr_point = points[i]
        path_length += np.sqrt((curr_point[0] - prev_point[0])**2 + (curr_point[1] - prev_point[1])**2)

    # 计算曲率半径
    if len(points) > 2:
        p1, p2, p3 = np.array(points[0]), np.array(points[len(points)//2]), np.array(points[-1])
        A = np.array([p1[:2], p2[:2], p3[:2]])
        curvature_radius = np.abs(np.linalg.det(np.vstack((A.T, np.ones((1,3))))) / (2 * np.linalg.norm(np.cross(p2[:2] - p1[:2], p3[:2] - p1[:2]))))
    
    total_loss = weights['w1'] * path_length + weights['w3'] * curvature_radius
    return total_loss

# 定义优化器
def optimizer(intersection_polygon, start_point, end_point, n_points=10):
    def objective_function(coords):
        points = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
        points = [point for point in points if intersection_polygon.contains(Point(point[0], point[1]))]
        if len(points) < 2:
            return float('inf')
        return evaluate_curve_quality(points)

    # 定义边界
    bounds = []
    for _ in range(n_points):
        bounds.append((intersection_polygon.bounds[0], intersection_polygon.bounds[2]))  # Longitude bounds
        bounds.append((intersection_polygon.bounds[1], intersection_polygon.bounds[3]))  # Latitude bounds

    result = differential_evolution(objective_function, bounds, strategy='best1bin', maxiter=1000, popsize=15, tol=0.01)
    optimized_coords = result.x

    optimized_path = [(optimized_coords[i], optimized_coords[i+1]) for i in range(0, len(optimized_coords), 2)]
    optimized_path = [point for point in optimized_path if intersection_polygon.contains(Point(point[0], point[1]))]

    return optimized_path, result.fun

# 处理路口数据
intersection_id = 'INT_94'
intersection_info = intersection_data[intersection_data['IntersectionID'] == intersection_id]
if intersection_info.empty:
    print(f"No data found for Intersection ID: {intersection_id}")

# 定义路口区域的多边形
intersection_polygon = Polygon(zip(intersection_info.iloc[0]['Longitude'], intersection_info.iloc[0]['Latitude']))

# 定义每个路径的起点和终点坐标范围（需要根据实际数据调整）
path_directions = {
    'left-right': [((intersection_polygon.bounds[0], (intersection_polygon.bounds[1] + intersection_polygon.bounds[3]) / 2), 
                   (intersection_polygon.bounds[2], (intersection_polygon.bounds[1] + intersection_polygon.bounds[3]) / 2))],
    'right-left': [((intersection_polygon.bounds[2], (intersection_polygon.bounds[1] + intersection_polygon.bounds[3]) / 2), 
                   (intersection_polygon.bounds[0], (intersection_polygon.bounds[1] + intersection_polygon.bounds[3]) / 2))],
    'up-right': [(((intersection_polygon.bounds[0] + intersection_polygon.bounds[2]) / 2, intersection_polygon.bounds[3]), 
                 (intersection_polygon.bounds[2], (intersection_polygon.bounds[1] + intersection_polygon.bounds[3]) / 2))],
    'right-up': [((intersection_polygon.bounds[2], (intersection_polygon.bounds[1] + intersection_polygon.bounds[3]) / 2), 
                 ((intersection_polygon.bounds[0] + intersection_polygon.bounds[2]) / 2, intersection_polygon.bounds[3]))],
    'up-left': [(((intersection_polygon.bounds[0] + intersection_polygon.bounds[2]) / 2, intersection_polygon.bounds[3]), 
                (intersection_polygon.bounds[0], (intersection_polygon.bounds[1] + intersection_polygon.bounds[3]) / 2))],
    'left-up': [((intersection_polygon.bounds[0], (intersection_polygon.bounds[1] + intersection_polygon.bounds[3]) / 2), 
                ((intersection_polygon.bounds[0] + intersection_polygon.bounds[2]) / 2, intersection_polygon.bounds[3]))]
}

optimized_paths = []

for direction, points in path_directions.items():
    for start_point, end_point in points:
        print(f"Optimizing path for direction: {direction}")

        optimized_path, min_loss = optimizer(intersection_polygon, start_point, end_point)
        optimized_paths.append((direction, optimized_path, min_loss))

# 打印优化后的路径
for direction, path, loss in optimized_paths:
    print(f"Direction: {direction}, Loss: {loss}")
    for coord in path:
        print(coord)

# 绘制优化后的路径
def plot_optimized_paths(intersection_id, optimized_paths):
    intersection_info = intersection_data[intersection_data['IntersectionID'] == intersection_id]
    if intersection_info.empty:
        print(f"No data found for Intersection ID: {intersection_id}")
        return None

    plt.figure(figsize=(12, 8))

    # 绘制路口边界
    for i in range(len(intersection_info)):
        plt.plot(intersection_info.iloc[i]['Longitude'], intersection_info.iloc[i]['Latitude'], marker='o', label=f'{intersection_id} Boundary')

    # 绘制所有优化后的路径
    for direction, optimized_path, min_loss in optimized_paths:
        lons, lats = zip(*optimized_path)
        plt.plot(lons, lats, marker='x', linestyle='-', label=f'Optimized Path {direction} (Loss: {min_loss:.2f})')

    plt.title(f'Optimized Paths for Intersection: {intersection_id}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.grid(True)
    plt.show()

# 绘制所有优化路径
plot_optimized_paths(intersection_id, optimized_paths)
