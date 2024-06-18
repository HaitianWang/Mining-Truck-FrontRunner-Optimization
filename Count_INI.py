import pandas as pd

# 加载CSV文件
file_path = 'B4_intersections.csv'
data = pd.read_csv(file_path)

# 计算不重复的路口标识符数量
unique_intersections = data['IntersectionID'].nunique()

print(f'{unique_intersections}')
