import pandas as pd
import numpy as np
import chardet
import logging
# 修复导入路径
from utils.logging_config import logger

def detect_encoding(file_path):
    """自动检测文件编码"""
    try:
        with open(file_path, 'rb') as f:
            raw = f.read(100000)
            result = chardet.detect(raw)
            return result['encoding']
    except Exception as e:
        logger.error(f"文件编码检测失败: {str(e)}")
        return 'gbk'  # 默认使用gbk编码

def load_etf_data(file_path='data/ETF行情数据.csv'):
    """加载并预处理ETF数据"""
    try:
        encoding = detect_encoding(file_path)
        logger.info(f"使用编码: {encoding} 加载文件: {file_path}")
        df = pd.read_csv(file_path, encoding=encoding)
        
        # 验证必要列
        required_cols = ['代码', '名称', '涨跌幅', '5日涨跌幅', '成交额', '换手率', '溢折率', '规模变化', '年初至今']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            logger.warning(f"数据文件缺少列: {', '.join(missing)}")
        
        # 预处理
        df = df.dropna(subset=['名称'])
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # 异常值处理
        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            median = df[col].median()
            df[col] = np.where(
                (df[col] < lower_bound) | (df[col] > upper_bound),
                median,
                df[col]
            )
        
        # 计算动量得分
        df['动量得分'] = 0.3 * df['涨跌幅'] + 0.7 * df['5日涨跌幅']
        
        logger.info(f"成功加载数据，共 {len(df)} 条记录")
        return df
    
    except Exception as e:
        logger.error(f"数据加载失败: {str(e)}", exc_info=True)
        raise
