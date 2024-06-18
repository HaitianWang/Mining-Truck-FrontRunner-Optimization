import pandas as pd
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

# 定义一个字典来存储每个路口通过的卡车信息
intersection_truck_pass = {}

# 遍历每个路口
for intersection_id in intersection_data['IntersectionID'].unique():
    intersection_info = intersection_data[intersection_data['IntersectionID'] == intersection_id]
    if intersection_info.empty:
        continue

    # 创建路口的多边形
    polygon = Polygon(zip(intersection_info.iloc[0]['Longitude'], intersection_info.iloc[0]['Latitude']))

    # 检查每辆卡车是否通过该路口
    for truck_id in truck_data['Truck'].unique():
        truck_movements = truck_data[truck_data['Truck'] == truck_id]
        truck_path = [Point(lon, lat) for lon, lat in zip(truck_movements['Longitude'], truck_movements['Latitude'])]
        
        passed_through_intersection = any(polygon.contains(point) for point in truck_path)
        
        if passed_through_intersection:
            if intersection_id not in intersection_truck_pass:
                intersection_truck_pass[intersection_id] = []
            intersection_truck_pass[intersection_id].append(truck_id)

# 将结果写入CSV文件
output_data = {'IntersectionID': [], 'Trucks': []}
for intersection_id, trucks in intersection_truck_pass.items():
    output_data['IntersectionID'].append(intersection_id)
    output_data['Trucks'].append(','.join(map(str, trucks)))

output_df = pd.DataFrame(output_data)
output_df.to_csv('intersection_truck_pass_on_order.csv', index=False)
