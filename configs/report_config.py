# 报告配置
REPORT_CONFIG = {
    'sections': [
        'market_overview',
        'performance_ranking',
        'opportunity_analysis',
        'portfolio_recommendation',
        'investment_strategy'
    ],
    'chart_sizes': {
        'histogram': (8, 4),  # 减小尺寸
        'bar_chart': (8, 5),
        'pie_chart': (6, 6)
    },
    'risk_free_rate': 0.02,  # 无风险利率，用于计算夏普比率
    'chart_dpi': 80  # 降低图表分辨率
}
