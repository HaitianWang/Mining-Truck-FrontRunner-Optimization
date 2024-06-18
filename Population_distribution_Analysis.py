import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from pyproj import Transformer
import numpy as np

# 定义转换器，将 WGS 84 UTM Zone 50S 转换为 WGS 84
transformer = Transformer.from_crs("epsg:32750", "epsg:4326")

# 加载数据集
intersection_file_path = 'B4_intersections_unique_valid.csv'
truck_file_path = 'B4_truck_movements_01.csv'
pass_file_path = 'Pass_INI_94.csv'

intersection_data = pd.read_csv(intersection_file_path, header=None, names=["IntersectionID", "Coordinates"])
truck_data = pd.read_csv(truck_file_path)
pass_data = pd.read_csv(pass_file_path)

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

# 将车辆移动数据集中的坐标从 UTM 转换为经纬度
truck_data['Latitude'], truck_data['Longitude'] = transformer.transform(truck_data['X'].values, truck_data['Y'].values)

# 定义损失函数
def calculate_loss(path_length, time_diff, curvature_radius, weights, means, stds):
    loss_path_length = (path_length - means['PathLength']) / stds['PathLength']
    loss_time_diff = (time_diff - means['TimeDiff']) / stds['TimeDiff']
    loss_curvature_radius = (curvature_radius - means['CurvatureRadius']) / stds['CurvatureRadius']
    total_loss = (weights['w1'] * loss_path_length) + (weights['w2'] * loss_time_diff) + (weights['w3'] * loss_curvature_radius)
    return total_loss

# 计算均值和标准差
means = {
    'PathLength': pass_data['PathLength'].mean(),
    'TimeDiff': pass_data['TimeDiff'].mean(),
    'CurvatureRadius': pass_data['CurvatureRadius'].mean()
}

stds = {
    'PathLength': pass_data['PathLength'].std(),
    'TimeDiff': pass_data['TimeDiff'].std(),
    'CurvatureRadius': pass_data['CurvatureRadius'].std()
}

# 设置权重
weights = {'w1': 0.3, 'w2': 0.3, 'w3': 0.4}

# 可视化函数
def plot_intersection_and_trucks(intersection_id, additional_points=1):
    intersection_info = intersection_data[intersection_data['IntersectionID'] == intersection_id]
    if intersection_info.empty:
        print(f"No data found for Intersection ID: {intersection_id}")
        return None

    plt.figure(figsize=(12, 8))

    # 绘制路口边界
    for i in range(len(intersection_info)):
        plt.plot(intersection_info.iloc[i]['Longitude'], intersection_info.iloc[i]['Latitude'], marker='o', label=f'{intersection_id} Boundary')

    # 获取路口边界的经纬度范围
    lat_min, lat_max = min(intersection_info.iloc[0]['Latitude']), max(intersection_info.iloc[0]['Latitude'])
    lon_min, lon_max = min(intersection_info.iloc[0]['Longitude']), max(intersection_info.iloc[0]['Longitude'])

    # 定义路口区域的多边形
    intersection_polygon = Polygon(zip(intersection_info.iloc[0]['Longitude'], intersection_info.iloc[0]['Latitude']))

    # 绘制通过路口的车辆轨迹
    for truck_id in truck_data['Truck'].unique():
        truck_movements = truck_data[truck_data['Truck'] == truck_id]
        truck_path = [Point(lon, lat) for lon, lat in zip(truck_movements['Longitude'], truck_movements['Latitude'])]
        
        # 筛选出车辆经过路口区域的轨迹点，并添加之前和之后的点
        passed_points = []
        for idx, point in enumerate(truck_path):
            if intersection_polygon.contains(point):
                start_idx = max(0, idx - additional_points)
                end_idx = min(len(truck_path), idx + additional_points + 1)
                passed_points.extend(truck_path[start_idx:end_idx])
                break
        
        if passed_points:
            lons, lats = zip(*[(p.x, p.y) for p in passed_points])
            plt.plot(lons, lats, marker='o', linestyle='-', label=f'Truck {truck_id}')
    
    plt.title(f'Intersection and Truck Movements Visualization: {intersection_id}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return intersection_polygon

# 输入路口标识符进行绘制
intersection_id = 'INT_94'
intersection_polygon = plot_intersection_and_trucks(intersection_id)

# 评估曲线质量
def evaluate_curve_quality(truck_movements, intersection_polygon):
    path_length = 0
    time_diff = pd.Timedelta(0)
    curvature_radius = 0
    points = []
    
    # 筛选通过交叉路口的轨迹点
    for _, row in truck_movements.iterrows():
        point = Point(row['Longitude'], row['Latitude'])
        if intersection_polygon.contains(point):
            points.append((row['Longitude'], row['Latitude'], row['TimeStamp']))
    
    if len(points) < 2:
        return None, "Not enough points within intersection polygon"

    # 计算路径长度和时间差
    for i in range(1, len(points)):
        prev_point = points[i-1]
        curr_point = points[i]
        path_length += np.sqrt((curr_point[0] - prev_point[0])**2 + (curr_point[1] - prev_point[1])**2)
        time_diff += pd.to_datetime(curr_point[2], format='%d %b %Y %H:%M:%S:%f') - pd.to_datetime(prev_point[2], format='%d %b %Y %H:%M:%S:%f')

    # 计算曲率半径（示例简单计算）
    if len(points) > 2:
        p1, p2, p3 = points[0], points[len(points)//2], points[-1]
        A = np.array([p1[:2], p2[:2], p3[:2]])
        curvature_radius = np.abs(np.linalg.det(np.vstack((A.T, np.ones((1,3))))) / (2 * np.linalg.norm(np.cross(p2[:2] - p1[:2], p3[:2] - p1[:2]))))
    
    time_diff = time_diff.total_seconds()
    
    # 检查限制条件
    for lon, lat, _ in points:
        point = Point(lon, lat)
        if not intersection_polygon.buffer(-6.92).contains(point):
            return None, "Path is too close to intersection edge"
    
    if path_length < 2.4:
        return None, "Path length is too short"
    
    return calculate_loss(path_length, time_diff, curvature_radius, weights, means, stds), None

# 评估每条曲线质量
results = []
for truck_id in truck_data['Truck'].unique():
    truck_movements = truck_data[truck_data['Truck'] == truck_id]
    loss, error = evaluate_curve_quality(truck_movements, intersection_polygon)
    if loss is not None:
        print(f'Truck {truck_id}: Loss = {loss}')
        results.append((truck_id, loss))
    else:
        print(f'Truck {truck_id}: {error}')

# 将结果保存为 DataFrame 并显示
results_df = pd.DataFrame(results, columns=['Truck', 'Loss'])
print(results_df)
