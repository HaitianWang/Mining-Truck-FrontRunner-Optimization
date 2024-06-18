import pandas as pd
import os

# 文件路径列表，假设文件存储在当前目录中
file_paths = [f'B4_truck_movements_{str(i).zfill(2)}.csv' for i in range(1, 55)]

# 标签行
header = ["Truck", "TimeStamp", "X", "Y"]

for file_path in file_paths:
    try:
        # 读取文件的前两行
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # 检查首行是否包含标签
        first_line = lines[0].strip()
        if first_line != ",".join(header):
            # 如果没有标签，添加标签
            with open(file_path, 'w') as file:
                file.write(",".join(header) + "\n")
                file.writelines(lines)
        
        print(f"Processed: {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
