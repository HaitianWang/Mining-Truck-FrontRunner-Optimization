import pandas as pd
import sys

# 设置标准输出为utf-8编码
sys.stdout.reconfigure(encoding='utf-8')

def analyze_csv(file_path):
    # 设置Pandas显示选项
    pd.set_option('display.max_columns', None)  # 显示所有列
    pd.set_option('display.max_rows', None)  # 显示所有行
    pd.set_option('display.max_colwidth', None)  # 显示列的最大宽度
    pd.set_option('display.width', None)  # 自动调整列宽
    
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 输出基本信息
    print("文件路径:", file_path)
    print("数据集基本信息:\n")
    
    # 行数和列数
    print("行数和列数:")
    print(df.shape)
    print("\n")
    
    # 每列的数据类型
    print("每列的数据类型:")
    print(df.dtypes)
    print("\n")
    
    # 缺失值统计
    print("缺失值统计:")
    print(df.isnull().sum())
    print("\n")
    
    # 描述性统计
    print("描述性统计:")
    print(df.describe(include='all'))
    print("\n")
    
    # 前五行数据预览
    print("前五行数据预览:")
    print(df.head())
    print("\n")

# 使用方法
file_path = 'B4_truck_movements.csv'
analyze_csv(file_path)
