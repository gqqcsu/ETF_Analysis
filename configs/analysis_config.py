# 分析权重配置
ANALYSIS_WEIGHTS = {
    '涨跌幅': 0.15,
    '5日涨跌幅': 0.20,
    '换手率': 0.15,
    '溢折率': 0.15,
    '年初至今': 0.20,
    '规模变化': 0.15
}

# 反转信号阈值
REVERSAL_THRESHOLD = {
    '5日跌幅': -0.02,  # 5日跌幅超过2%
    '今日涨幅': 0.00    # 今日上涨
}

# 折价阈值
DISCOUNT_THRESHOLD = -0.005  # 折价超过0.5%
