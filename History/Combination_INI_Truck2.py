import pandas as pd
import matplotlib.pyplot as plt

# 加载路口数据集
intersection_file_path = 'B4_intersections_unique_valid.csv'
intersection_data = pd.read_csv(intersection_file_path)

# 处理 Coordinates 列
intersection_data['Coordinates'] = intersection_data['Coordinates'].str.replace('LINESTRING\(', '', regex=True).str.replace('\)', '', regex=True)

# 定义一个函数，将坐标分割为单独的纬度和经度列表
def split_coordinates(coord_string):
    latitudes = []
    longitudes = []
    for coord in coord_string.split(','):
        try:
            lat, lon = map(float, coord.split())
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
truck_file_path = 'B4_truck_movements_10.csv'
truck_data = pd.read_csv(truck_file_path)

# 定义可视化函数
def plot_intersection_and_trucks(intersection_id):
    intersection_info = intersection_data[intersection_data['IntersectionID'] == intersection_id]
    if intersection_info.empty:
        print(f"No data found for Intersection ID: {intersection_id}")
        return

    plt.figure(figsize=(12, 8))

    # 绘制路口边界
    for i in range(len(intersection_info)):
        plt.plot(intersection_info.iloc[i]['Latitude'], intersection_info.iloc[i]['Longitude'], marker='o', label=f'{intersection_id} Boundary')

    # 获取路口边界的经纬度范围
    lat_min, lat_max = min(intersection_info.iloc[0]['Latitude']), max(intersection_info.iloc[0]['Latitude'])
    lon_min, lon_max = min(intersection_info.iloc[0]['Longitude']), max(intersection_info.iloc[0]['Longitude'])

    # 绘制通过路口的车辆轨迹
    for truck_id in truck_data['Truck'].unique():
        truck_movements = truck_data[truck_data['Truck'] == truck_id]
        # 筛选出车辆经过路口区域的轨迹点
        mask = (
            (truck_movements['X'] >= lat_min) & (truck_movements['X'] <= lat_max) &
            (truck_movements['Y'] >= lon_min) & (truck_movements['Y'] <= lon_max)
        )
        truck_movements_through_intersection = truck_movements[mask]
        if not truck_movements_through_intersection.empty:
            plt.plot(truck_movements_through_intersection['X'], truck_movements_through_intersection['Y'], marker='o', linestyle='-')

    plt.title(f'Intersection and Truck Movements Visualization: {intersection_id}')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.grid(True)
    plt.show()

# 输入路口标识符进行绘制
intersection_id = 'INT_02'
plot_intersection_and_trucks(intersection_id)
