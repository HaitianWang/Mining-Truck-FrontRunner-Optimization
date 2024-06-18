import pandas as pd
import matplotlib.pyplot as plt

# 加载数据集
file_path = 'B4_intersections_unique_valid.csv'  # 请将此路径替换为您自己的文件路径
data = pd.read_csv(file_path, header=None, names=["IntersectionID", "Coordinates"])

# 处理 Coordinates 列
data['Coordinates'] = data['Coordinates'].str.replace('LINESTRING\(', '', regex=True).str.replace('\)', '', regex=True)

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
            # 跳过不符合格式的坐标
            continue
    return latitudes, longitudes

# 应用函数以拆分坐标
data['Latitude'], data['Longitude'] = zip(*data['Coordinates'].apply(split_coordinates))

# 移除空的列表
data = data[data['Latitude'].map(len) > 0]

# 判断是否是闭合曲线
def is_closed_curve(latitudes, longitudes):
    return latitudes[0] == latitudes[-1] and longitudes[0] == longitudes[-1]

# 打印特定路口的数据
def print_intersection_data(intersection_id):
    intersection_data = data[data['IntersectionID'] == intersection_id]
    if intersection_data.empty:
        print(f"No data found for Intersection ID: {intersection_id}")
    else:
        print(intersection_data)

# 可视化函数
def plot_intersection(intersection_id):
    intersection_data = data[data['IntersectionID'] == intersection_id]
    if intersection_data.empty:
        print(f"No data found for Intersection ID: {intersection_id}")
        return
    plt.figure(figsize=(12, 8))
    for i in range(len(intersection_data)):
        latitudes = intersection_data.iloc[i]['Latitude']
        longitudes = intersection_data.iloc[i]['Longitude']
        if is_closed_curve(latitudes, longitudes):
            plt.plot(latitudes, longitudes, marker='o')
    plt.title(f'Intersection Visualization: {intersection_id}')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.grid(True)
    plt.show()

# 输入路口标识符进行绘制和检查数据
intersection_id = 'INT_100'  # 您可以根据需要修改此标识符
print_intersection_data(intersection_id)
plot_intersection(intersection_id)
