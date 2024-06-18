import pandas as pd

# 加载CSV文件
file_path = 'B4_truck_movements_01.csv'
data = pd.read_csv(file_path)

# 计算不重复的卡车的数量
unique_intersections = data['Truck'].nunique()

print(f'{unique_intersections}')
