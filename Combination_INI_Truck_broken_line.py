import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from pyproj import Transformer

# 定义转换器，将 WGS 84 UTM Zone 50S 转换为 WGS 84
transformer = Transformer.from_crs("epsg:32750", "epsg:4326")

# 加载路口数据集
intersection_file_path = 'B4_intersections_unique_valid.csv'
intersection_data = pd.read_csv(intersection_file_path, header=None, names=["IntersectionID", "Coordinates"])

# 处理 Coordinates 列
intersection_data['Coordinates'] = intersection_data['Coordinates'].str.replace('LINESTRING\(', '', regex=True).str.replace('\)', '', regex=True)

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

# 加载车辆移动数据集
truck_file_path = 'B4_truck_movements_01.csv'
truck_data = pd.read_csv(truck_file_path)

# 将车辆移动数据集中的坐标从 UTM 转换为经纬度
truck_data['Latitude'], truck_data['Longitude'] = transformer.transform(truck_data['X'].values, truck_data['Y'].values)

# 定义可视化函数
def plot_intersection_and_trucks(intersection_id, additional_points=1):
    intersection_info = intersection_data[intersection_data['IntersectionID'] == intersection_id]
    if intersection_info.empty:
        print(f"No data found for Intersection ID: {intersection_id}")
        return

    plt.figure(figsize=(12, 8))

    # 绘制路口边界
    for i in range(len(intersection_info)):
        plt.plot(intersection_info.iloc[i]['Longitude'], intersection_info.iloc[i]['Latitude'], marker='o', label=f'{intersection_id} Boundary')

    # 获取路口边界的经纬度范围
    lat_min, lat_max = min(intersection_info.iloc[0]['Latitude']), max(intersection_info.iloc[0]['Latitude'])
    lon_min, lon_max = min(intersection_info.iloc[0]['Longitude']), max(intersection_info.iloc[0]['Longitude'])

    # 定义路口区域的多边形
    polygon = Polygon(zip(intersection_info.iloc[0]['Longitude'], intersection_info.iloc[0]['Latitude']))

    # 绘制通过路口的车辆轨迹
    for truck_id in truck_data['Truck'].unique():
        truck_movements = truck_data[truck_data['Truck'] == truck_id]
        truck_path = [Point(lon, lat) for lon, lat in zip(truck_movements['Longitude'], truck_movements['Latitude'])]
        
        # 筛选出车辆经过路口区域的轨迹点，并添加之前和之后的点
        passed_points = []
        for idx, point in enumerate(truck_path):
            if polygon.contains(point):
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

# 输入路口标识符进行绘制
intersection_id = 'INT_94'
plot_intersection_and_trucks(intersection_id)
