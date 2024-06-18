import pandas as pd

# 文件路径列表，假设文件存储在当前目录中
file_paths = [f'B4_truck_movements_{str(i).zfill(2)}.csv' for i in range(1, 55)]

# 标签行
header = ["Truck", "TimeStamp", "X", "Y"]

for file_path in file_paths:
    try:
        # 使用 utf-8-sig 编码读取文件，去除BOM
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # 检查文件是否已经包含了正确的标签行
        if list(df.columns) != header:
            df.columns = header
        
        # 重新保存文件，确保没有BOM
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"Processed: {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
