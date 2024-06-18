import pandas as pd
import matplotlib.pyplot as plt

# 加载数据集
file_path = 'B4_110[100].csv'  
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

# 打印检查数据以确认正确处理
print(data.head())

# 可视化函数
def plot_intersections(data):
    plt.figure(figsize=(12, 8))
    for i in range(len(data)):
        plt.plot(data.iloc[i]['Latitude'], data.iloc[i]['Longitude'], marker='o')
    plt.title('Intersections Visualization')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.grid(True)
    plt.show()

# 绘制交叉路口
plot_intersections(data)
