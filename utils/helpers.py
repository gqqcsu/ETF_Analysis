import base64
from io import BytesIO
import matplotlib.pyplot as plt

def fig_to_base64(fig):
    """将matplotlib图表转为base64编码"""
    img = BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

def format_percentage(value):
    """格式化百分比显示"""
    return f"{value:.2%}"

def format_currency(value):
    """格式化货币金额（亿元）"""
    return f"{value/100000000:.2f}"

def create_combined_chart(df, analysis_results):
    """创建组合图表"""
    # 创建多图表布局
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # 涨跌幅分布
    axs[0, 0].hist(df['涨跌幅'], bins=50, alpha=0.7)
    axs[0, 0].set_title('ETF涨跌幅分布')
    axs[0, 0].set_xlabel('涨跌幅')
    axs[0, 0].set_ylabel('数量')
    
    # 类型平均涨跌幅
    type_perf = analysis_results['type_perf']
    type_perf['平均涨跌幅'].head(10).plot(kind='bar', ax=axs[0, 1], color='skyblue')
    axs[0, 1].set_title('不同类型ETF平均涨跌幅')
    axs[0, 1].set_ylabel('平均涨跌幅')
    axs[0, 1].set_xlabel('ETF类型')
    axs[0, 1].tick_params(axis='x', rotation=45)
    
    # 成交额TOP10
    top_volume = analysis_results['top_volume'].set_index('名称')['成交额']
    top_volume = top_volume / top_volume.sum() * 100
    top_volume.plot(kind='pie', ax=axs[1, 0], autopct='%1.1f%%')
    axs[1, 0].set_title('成交额TOP10 ETF占比')
    axs[1, 0].set_ylabel('')
    
    # 综合评分TOP10
    if '综合得分' in df.columns:
        top_score = df.nlargest(10, '综合得分')
        axs[1, 1].barh(top_score['名称'], top_score['综合得分'], color='green')
        axs[1, 1].set_title('综合评分TOP10 ETF')
        axs[1, 1].set_xlabel('综合得分')
    
    plt.tight_layout()
    return fig_to_base64(fig)
