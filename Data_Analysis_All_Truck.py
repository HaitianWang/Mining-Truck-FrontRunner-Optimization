import pandas as pd
from shapely.geometry import Point, Polygon, LineString
from pyproj import Transformer
import math
import os

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

# 特定路口ID
intersection_id = 'INT_94'
intersection_info = intersection_data[intersection_data['IntersectionID'] == intersection_id]

# 创建路口的多边形
polygon = Polygon(zip(intersection_info.iloc[0]['Longitude'], intersection_info.iloc[0]['Latitude']))

# 定义一个函数来计算两点之间的距离
def haversine(lat1, lon1, lat2, lon2):
    R = 6371e3  # 地球半径，单位米
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 结果列表
all_results = []

# 遍历所有卡车移动数据集
for i in range(1, 55):
    truck_file_path = f'B4_truck_movements_{i:02d}.csv'
    if not os.path.exists(truck_file_path):
        print(f"File {truck_file_path} does not exist.")
        continue

    truck_data = pd.read_csv(truck_file_path)

    # 将车辆移动数据集中的坐标从 UTM 转换为经纬度
    truck_data['Latitude'], truck_data['Longitude'] = transformer.transform(truck_data['X'].values, truck_data['Y'].values)

    # 转换TimeStamp为日期时间格式
    truck_data['TimeStamp'] = pd.to_datetime(truck_data['TimeStamp'], format='%d %b %Y %H:%M:%S:%f')

    # 检查每辆卡车是否通过该路口
    for truck_id in truck_data['Truck'].unique():
        truck_movements = truck_data[truck_data['Truck'] == truck_id]
        truck_path = [Point(lon, lat) for lon, lat in zip(truck_movements['Longitude'], truck_movements['Latitude'])]
        timestamps = truck_movements['TimeStamp'].tolist()
        
        in_intersection = False
        entry_idx = None
        exit_idx = None
        
        for idx, point in enumerate(truck_path):
            if polygon.contains(point):
                if not in_intersection:
                    # 卡车进入路口
                    entry_idx = max(0, idx - 1)
                    in_intersection = True
            else:
                if in_intersection:
                    # 卡车离开路口
                    exit_idx = min(len(truck_path) - 1, idx)
                    
                    # 记录通过事件
                    entry_point = truck_path[entry_idx]
                    exit_point = truck_path[exit_idx]
                    intersection_points = truck_path[entry_idx+1:exit_idx]
                    
                    # 计算路径长度
                    path_length = 0
                    points = [entry_point] + intersection_points + [exit_point]
                    for i in range(len(points) - 1):
                        path_length += haversine(points[i].y, points[i].x, points[i + 1].y, points[i + 1].x)
                    
                    # 计算通过时间
                    entry_time = timestamps[entry_idx]
                    exit_time = timestamps[exit_idx]
                    time_diff = (exit_time - entry_time).total_seconds()
                    
                    # 计算转向角度（曲率半径）
                    line = LineString([p.coords[0] for p in truck_path[entry_idx:exit_idx+1]])
                    intersection = polygon.intersection(line)
                    
                    curvature_radius = '无法计算'
                    if intersection.type == 'LineString':
                        intersection_coords = list(intersection.coords)
                        if len(intersection_coords) >= 3:
                            entry_point = intersection_coords[0]
                            mid_point = intersection_coords[len(intersection_coords) // 2]
                            exit_point = intersection_coords[-1]
                            
                            a = haversine(entry_point[1], entry_point[0], mid_point[1], mid_point[0])
                            b = haversine(mid_point[1], mid_point[0], exit_point[1], exit_point[0])
                            c = haversine(entry_point[1], entry_point[0], exit_point[1], exit_point[0])
                            
                            # 使用余弦定理计算曲率半径
                            try:
                                curvature_radius = (a * b * c) / math.sqrt((a+b+c)*(b+c-a)*(c+a-b)*(a+b-c))
                            except ZeroDivisionError:
                                curvature_radius = float('inf')
                    
                    all_results.append([truck_id, [(entry_point[0], entry_point[1]), (exit_point[0], exit_point[1])], path_length, time_diff, curvature_radius])
                    
                    # 重置标志位
                    in_intersection = False
                    entry_idx = None
                    exit_idx = None

# 将所有结果写入CSV文件
output_df = pd.DataFrame(all_results, columns=['Truck', 'Coordinates', 'PathLength', 'TimeDiff', 'CurvatureRadius'])
output_df.to_csv('Pass_INI_ALL.csv', index=False)

print("Analysis complete. Results saved to Pass_INI_ALL.csv.")
