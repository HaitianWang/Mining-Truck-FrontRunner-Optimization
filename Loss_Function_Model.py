import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import haversine_distances

# 加载数据
intersections_df = pd.read_csv('/mnt/data/B4_intersections_unique_valid.csv')
truck_movements_df = pd.read_csv('/mnt/data/B4_truck_movements_01.csv')

# 转换时间戳为日期时间格式
truck_movements_df['TimeStamp'] = pd.to_datetime(truck_movements_df['TimeStamp'], format='%d %b %Y %H:%M:%S:%f')

# 损失函数模型的参数
def compute_loss(path_length, time_diff, curvature_radius, w1=0.3, w2=0.3, w3=0.4):
    return w1 * path_length + w2 * time_diff + w3 * (1 / (curvature_radius + 1e-5))  # 避免除以零

# 计算路径长度
def calculate_path_length(coords):
    total_length = 0.0
    for i in range(1, len(coords)):
        total_length += haversine_distances([coords[i-1], coords[i]])[0][1] * 6371000  # 转换为米
    return total_length

# 计算曲率半径（这里假设使用每个点的曲率半径的平均值）
def calculate_curvature_radius(coords):
    radii = []
    for i in range(1, len(coords)-1):
        p1, p2, p3 = coords[i-1], coords[i], coords[i+1]
        a = haversine_distances([p1, p2])[0][1] * 6371000
        b = haversine_distances([p2, p3])[0][1] * 6371000
        c = haversine_distances([p3, p1])[0][1] * 6371000
        s = (a + b + c) / 2
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        radius = (a * b * c) / (4 * area + 1e-5)  # 避免除以零
        radii.append(radius)
    return np.mean(radii)

# 计算每条道路曲线的评分
def evaluate_curves(intersections_df, truck_movements_df):
    results = []
    for index, row in intersections_df.iterrows():
        intersection_id = row['IntersectionID']
        geo_string = row['Coordinates']
        coords = [tuple(map(float, coord.split())) for coord in geo_string.split('(')[1].strip(')').split(',')]
        
        path_length = calculate_path_length(coords)
        curvature_radius = calculate_curvature_radius(coords)
        
        # 过滤经过这个路口的卡车数据
        trucks_at_intersection = truck_movements_df[
            (truck_movements_df['X'] >= min([c[0] for c in coords])) &
            (truck_movements_df['X'] <= max([c[0] for c in coords])) &
            (truck_movements_df['Y'] >= min([c[1] for c in coords])) &
            (truck_movements_df['Y'] <= max([c[1] for c in coords]))
        ]
        
        time_diff = (trucks_at_intersection['TimeStamp'].max() - trucks_at_intersection['TimeStamp'].min()).total_seconds()
        
        loss = compute_loss(path_length, time_diff, curvature_radius)
        results.append((intersection_id, path_length, time_diff, curvature_radius, loss))
    
    results_df = pd.DataFrame(results, columns=['IntersectionID', 'PathLength', 'TimeDiff', 'CurvatureRadius', 'Loss'])
    return results_df

# 评估曲线
results_df = evaluate_curves(intersections_df, truck_movements_df)
print(results_df)

# 保存结果到CSV文件
results_df.to_csv('/mnt/data/curve_evaluation_results.csv', index=False)
