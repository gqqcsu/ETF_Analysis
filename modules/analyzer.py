import numpy as np
from scipy import stats
import pandas as pd
from configs.analysis_config import ANALYSIS_WEIGHTS, REVERSAL_THRESHOLD, DISCOUNT_THRESHOLD

def calculate_composite_score(df):
    """计算ETF综合得分"""
    factors = list(ANALYSIS_WEIGHTS.keys())
    df_factors = df[factors].copy()
    
    # Z-score标准化处理
    for factor in factors:
        # 处理无穷大值
        df_factors[factor] = df_factors[factor].replace([np.inf, -np.inf], np.nan)
        # Z-score标准化
        z_scores = stats.zscore(df_factors[factor], nan_policy='omit')
        # 将NaN替换为0
        df_factors[factor] = np.nan_to_num(z_scores, nan=0)
    
    # 计算加权综合得分
    composite_score = np.zeros(len(df))
    for factor, weight in ANALYSIS_WEIGHTS.items():
        composite_score += df_factors[factor] * weight
    
    return composite_score

def analyze_etf_data(df):
    """执行完整的ETF数据分析"""
    results = {}
    
    # 1. 计算综合得分
    df['综合得分'] = calculate_composite_score(df)
    
    # 2. 涨跌幅排名
    results['top_gainers'] = df.nlargest(10, '涨跌幅')[['代码', '名称', '现价', '涨跌幅', '成交额']]
    results['top_losers'] = df.nsmallest(10, '涨跌幅')[['代码', '名称', '现价', '涨跌幅', '成交额']]
    
    # 3. 成交额排名
    results['top_volume'] = df.nlargest(10, '成交额')[['代码', '名称', '现价', '涨跌幅', '成交额']]
    
    # 4. 换手率排名
    results['top_turnover'] = df.nlargest(10, '换手率')[['代码', '名称', '现价', '换手率', '成交额']]
    
    # 5. 折价ETF分析
    results['discount_etfs'] = df[df['溢折率'] < DISCOUNT_THRESHOLD].sort_values('溢折率')[
        ['代码', '名称', '现价', '溢折率', '成交额', '换手率']].head(10)
    
    # 6. 资金流入排名
    results['top_inflow'] = df.nlargest(10, '规模变化')[['代码', '名称', '现价', '规模变化', '估算规模', '涨跌幅']]
    
    # 7. 反转信号ETF
    df['反转信号'] = (df['5日涨跌幅'] < REVERSAL_THRESHOLD['5日跌幅']) & (df['涨跌幅'] > REVERSAL_THRESHOLD['今日涨幅'])
    results['reversal_etfs'] = df[df['反转信号']].sort_values('5日涨跌幅')[
        ['代码', '名称', '现价', '涨跌幅', '5日涨跌幅', '成交额']].head(10)
    
    # 8. 综合评分排名
    results['top_score'] = df.nlargest(10, '综合得分')[
        ['代码', '名称', '现价', '涨跌幅', '5日涨跌幅', '年初至今', '综合得分']]
    
    # 9. 类型分析
    results['type_perf'] = df.groupby('类型')['涨跌幅'].agg(['mean', 'count'])
    results['type_perf'].columns = ['平均涨跌幅', '数量']
    
    # 10. 市场概况
    results['market_overview'] = {
        '上涨': len(df[df['涨跌幅'] > 0]),
        '下跌': len(df[df['涨跌幅'] < 0]),
        '平盘': len(df[df['涨跌幅'] == 0]),
        '平均涨跌幅': df['涨跌幅'].mean(),
        '总数量': len(df)
    }
    
    return results
