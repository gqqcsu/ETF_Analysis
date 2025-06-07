import os
import glob
import argparse
from utils.logging_config import logger

def find_data_files():
    """在data目录中查找可能的ETF数据文件"""
    data_dir = 'data'
    if not os.path.exists(data_dir):
        return []
    
    # 支持的文件扩展名
    extensions = ['*.xlsx', '*.xls', '*.csv']
    
    found_files = []
    for ext in extensions:
        found_files.extend(glob.glob(os.path.join(data_dir, ext)))
    
    return found_files

def main():
    parser = argparse.ArgumentParser(description='查找ETF数据文件')
    parser.add_argument('--list', action='store_true', help='列出找到的数据文件')
    args = parser.parse_args()
    
    files = find_data_files()
    
    if args.list:
        if files:
            print("找到以下数据文件:")
            for file in files:
                print(f"  - {file}")
        else:
            print("在data目录中未找到任何CSV或Excel文件")
    else:
        if files:
            print(f"建议使用以下数据文件: {files[0]}")
            print("运行程序时指定文件: python main.py \"{files[0]}\"")
        else:
            print("在data目录中未找到任何CSV或Excel文件")
            print("请将数据文件放入data目录并命名为: ETF行情数据.xlsx 或类似名称")

if __name__ == "__main__":
    main()
