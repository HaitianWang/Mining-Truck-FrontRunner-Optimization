import pandas as pd

# 加载数据集
file_path = 'B4_intersections.csv'  # 请将此路径替换为您自己的文件路径
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

# 筛选出闭合曲线的数据
valid_intersections = data[data.apply(lambda row: is_closed_curve(row['Latitude'], row['Longitude']), axis=1)]

# 将筛选出的数据保存到新的 CSV 文件中
valid_intersections[['IntersectionID', 'Coordinates']].to_csv('B4_intersections_valid.csv', index=False)

print("Valid intersection boundary data has been saved to B4_intersections_valid.csv.")
