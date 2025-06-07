import base64
from datetime import datetime
import os
import pandas as pd
import jinja2
from configs.report_config import REPORT_CONFIG
import logging
from utils.logging_config import logger
import traceback

# 设置Jinja2环境
template_loader = jinja2.FileSystemLoader(searchpath='./templates')
template_env = jinja2.Environment(loader=template_loader)

def format_percentage(value):
    """格式化百分比显示"""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"{value:.2%}"

def format_currency(value):
    """格式化货币金额（亿元）"""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"{value/100000000:.2f}"

def format_value(value, decimals=3):
    """通用格式化函数"""
    if pd.isna(value) or value is None:
        return "N/A"
    elif isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)

def generate_markdown_report(analysis_results, charts, portfolio_advice, file_path=None):
    """生成Markdown格式的日报"""
    try:
        today = datetime.now().strftime('%Y年%m月%d日')
        
        # 获取市场概况
        market = analysis_results.get('market_overview', {})
        total_etfs = market.get('总数量', market.get('上涨', 0) + market.get('下跌', 0) + market.get('平盘', 0))
        
        # 创建报告内容
        md_content = f"""# ETF市场日报 | {today}

## 一、市场概览

今日市场共有{total_etfs}只ETF交易，**{market.get('上涨', 0)}**只上涨，**{market.get('下跌', 0)}**只下跌，**{market.get('平盘', 0)}**只平盘，平均涨幅**{format_percentage(market.get('平均涨跌幅', 0))}**。
"""
        
        # 添加涨跌幅分布图（如果有）
        if 'price_change_dist' in charts and charts['price_change_dist']:
            md_content += f"\n\n![ETF涨跌幅分布](data:image/png;base64,{charts['price_change_dist']})"
        
        # 添加类型平均涨跌幅图（如果有）
        if 'type_performance' in charts and charts['type_performance']:
            md_content += f"\n\n### 各类ETF表现\n\n![不同类型ETF平均涨跌幅](data:image/png;base64,{charts['type_performance']})"
        
        md_content += """
## 二、ETF龙虎榜

### 涨幅榜 TOP10 🚀

| 代码 | 名称 | 现价 | 涨跌幅 | 成交额(亿元) |
|------|------|------|--------|--------------|
"""
        # 添加涨幅榜
        top_gainers = analysis_results.get('top_gainers', pd.DataFrame())
        if not top_gainers.empty:
            for _, row in top_gainers.iterrows():
                md_content += f"| {row['代码']} | {row['名称']} | {format_value(row.get('现价', 0))} | {format_percentage(row.get('涨跌幅', 0))} | {format_currency(row.get('成交额', 0))} |\n"
        else:
            md_content += "| - | 无数据 | - | - | - |\n"
        
        md_content += """
### 跌幅榜 TOP10 📉

| 代码 | 名称 | 现价 | 涨跌幅 | 成交额(亿元) |
|------|------|------|--------|--------------|
"""
        # 添加跌幅榜
        top_losers = analysis_results.get('top_losers', pd.DataFrame())
        if not top_losers.empty:
            for _, row in top_losers.iterrows():
                md_content += f"| {row['代码']} | {row['名称']} | {format_value(row.get('现价', 0))} | {format_percentage(row.get('涨跌幅', 0))} | {format_currency(row.get('成交额', 0))} |\n"
        else:
            md_content += "| - | 无数据 | - | - | - |\n"
        
        md_content += """
### 成交额 TOP10 💰

| 代码 | 名称 | 现价 | 涨跌幅 | 成交额(亿元) |
|------|------|------|--------|--------------|
"""
        # 添加成交额排名
        top_volume = analysis_results.get('top_volume', pd.DataFrame())
        if not top_volume.empty:
            for _, row in top_volume.iterrows():
                md_content += f"| {row['代码']} | {row['名称']} | {format_value(row.get('现价', 0))} | {format_percentage(row.get('涨跌幅', 0))} | {format_currency(row.get('成交额', 0))} |\n"
        else:
            md_content += "| - | 无数据 | - | - | - |\n"
        
        # 添加成交额占比图（如果有）
        if 'volume_dist' in charts and charts['volume_dist']:
            md_content += f"\n\n![成交额TOP10占比](data:image/png;base64,{charts['volume_dist']})"
        
        md_content += """
### 换手率 TOP10 🔄

| 代码 | 名称 | 现价 | 换手率 | 成交额(亿元) |
|------|------|------|--------|--------------|
"""
        # 添加换手率排名
        top_turnover = analysis_results.get('top_turnover', pd.DataFrame())
        if not top_turnover.empty:
            for _, row in top_turnover.iterrows():
                md_content += f"| {row['代码']} | {row['名称']} | {format_value(row.get('现价', 0))} | {format_percentage(row.get('换手率', 0))} | {format_currency(row.get('成交额', 0))} |\n"
        else:
            md_content += "| - | 无数据 | - | - | - |\n"
        
        md_content += """
## 三、投资机会挖掘

### 溢价折价机会 💎

以下ETF存在较大折价，可能存在投资价值：

| 代码 | 名称 | 现价 | 溢折率 | 成交额(亿元) |
|------|------|------|--------|--------------|
"""
        # 添加折价ETF
        discount_etfs = analysis_results.get('discount_etfs', pd.DataFrame())
        if not discount_etfs.empty:
            for _, row in discount_etfs.iterrows():
                md_content += f"| {row['代码']} | {row['名称']} | {format_value(row.get('现价', 0))} | {format_percentage(row.get('溢折率', 0))} | {format_currency(row.get('成交额', 0))} |\n"
        else:
            md_content += "| - | 暂无明显折价ETF | - | - | - |\n"
        
        md_content += """
### 资金流入 TOP10 💵

| 代码 | 名称 | 现价 | 资金流入(亿元) | 涨跌幅 |
|------|------|------|----------------|--------|
"""
        # 添加资金流入排名
        top_inflow = analysis_results.get('top_inflow', pd.DataFrame())
        if not top_inflow.empty:
            for _, row in top_inflow.iterrows():
                md_content += f"| {row['代码']} | {row['名称']} | {format_value(row.get('现价', 0))} | {format_currency(row.get('规模变化', 0))} | {format_percentage(row.get('涨跌幅', 0))} |\n"
        else:
            md_content += "| - | 无数据 | - | - | - |\n"
        
        md_content += """
### 潜在反转信号 📊

以下ETF 5日跌幅较大但今日上涨，可能出现技术性反转：

| 代码 | 名称 | 现价 | 今日涨跌幅 | 5日涨跌幅 |
|------|------|------|------------|-----------|
"""
        # 添加反转信号ETF
        reversal_etfs = analysis_results.get('reversal_etfs', pd.DataFrame())
        if not reversal_etfs.empty:
            for _, row in reversal_etfs.iterrows():
                md_content += f"| {row['代码']} | {row['名称']} | {format_value(row.get('现价', 0))} | {format_percentage(row.get('涨跌幅', 0))} | {format_percentage(row.get('5日涨跌幅', 0))} |\n"
        else:
            md_content += "| - | 暂无明显反转信号ETF | - | - | - |\n"
        
        md_content += """
### 综合评分 TOP10 🏆

基于多因子模型（涨跌幅、5日涨跌幅、换手率、溢折率、年初至今表现、资金流向等）评分最高的ETF：

| 代码 | 名称 | 现价 | 涨跌幅 | 5日涨跌幅 | 年初至今 | 综合得分 |
|------|------|------|--------|-----------|----------|----------|
"""
        # 添加综合评分排名 - 修复了括号错误
        top_score = analysis_results.get('top_score', pd.DataFrame())
        if not top_score.empty:
            for _, row in top_score.iterrows():
                md_content += f"| {row['代码']} | {row['名称']} | {format_value(row.get('现价', 0))} | {format_percentage(row.get('涨跌幅', 0))} | {format_percentage(row.get('5日涨跌幅', 0))} | {format_percentage(row.get('年初至今', 0))} | {format_value(row.get('综合得分', 0), 2)} |\n"
        else:
            md_content += "| - | 无数据 | - | - | - | - | - |\n"
        
        # 添加综合评分散点图（如果有）
        if 'score_scatter' in charts and charts['score_scatter']:
            md_content += f"\n\n![ETF综合得分 vs 成交额](data:image/png;base64,{charts['score_scatter']})"
        
        md_content += """
## 四、ETF投资组合建议

根据ETF综合表现，我们按不同行业筛选出以下值得关注的ETF：
"""
        
        # 添加行业分类推荐
        if portfolio_advice:
            # 确保PORTFOLIO_CATEGORIES存在
            try:
                from configs.portfolio_config import PORTFOLIO_CATEGORIES
            except ImportError:
                PORTFOLIO_CATEGORIES = {
                    '科技类': [], '金融类': [], '消费类': [], 
                    '医药类': [], '大宗商品': [], '其他': []
                }
            
            for category in PORTFOLIO_CATEGORIES.keys():
                md_content += f"\n### {category}ETF\n"
                etfs = portfolio_advice.get(category, pd.DataFrame())
                if not etfs.empty:
                    for _, row in etfs.iterrows():
                        md_content += f"- **{row['名称']}** ({row['代码']})：现价 {format_value(row.get('现价', 0))}，涨跌幅 {format_percentage(row.get('涨跌幅', 0))}，综合得分 {format_value(row.get('综合得分', 0), 2)}\n"
                else:
                    md_content += "- 暂无推荐\n"
        else:
            md_content += "\n暂无投资组合建议\n"
        
        # 结束部分
        md_content += f"""
## 五、投资策略建议

### 短期策略

1. **关注反转信号ETF**：对于5日跌幅较大但今日上涨的ETF，可能出现短期反弹机会，适合短线交易者关注。
2. **高换手率ETF**：换手率较高的ETF表明交投活跃，短期可能有较大波动，提供交易机会。

### 中长期策略

1. **关注低估值ETF**：寻找具备折价和低估值属性的ETF，长期持有可能获得更好的投资回报。
2. **资金持续流入ETF**：持续获得资金流入的ETF通常基本面较好，适合中长期配置。
3. **综合评分高的ETF**：多因子综合表现优异的ETF，通常具备较好的投资价值。

### 风险提示

- 过去表现不代表未来，投资需谨慎
- 市场波动可能导致短期亏损
- 投资前请充分了解产品特性
- 本报告不构成投资建议，仅供参考

---

*以上数据基于{today}收盘数据分析，仅供参考，不构成投资建议。*
"""
        
        # 保存到文件
        if file_path is None:
            file_path = f"reports/ETF市场日报_{datetime.now().strftime('%Y%m%d')}.md"
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"已生成ETF市场日报：{file_path}")
        return md_content
    
    except Exception as e:
        logger.error(f"生成Markdown报告失败: {str(e)}\n{traceback.format_exc()}")
        return "报告生成失败"

def generate_html_report(analysis_results, charts, portfolio_advice, output_file=None):
    """生成HTML格式的报告"""
    try:
        today = datetime.now().strftime('%Y年%m月%d日')
        
        # 准备模板数据
        report_data = {
            'report_date': today,
            'market': analysis_results.get('market_overview', {}),
            'top_gainers': analysis_results.get('top_gainers', pd.DataFrame()).to_dict(orient='records'),
            'top_losers': analysis_results.get('top_losers', pd.DataFrame()).to_dict(orient='records'),
            'top_volume': analysis_results.get('top_volume', pd.DataFrame()).to_dict(orient='records'),
            'top_turnover': analysis_results.get('top_turnover', pd.DataFrame()).to_dict(orient='records'),
            'discount_etfs': analysis_results.get('discount_etfs', pd.DataFrame()).to_dict(orient='records'),
            'reversal_etfs': analysis_results.get('reversal_etfs', pd.DataFrame()).to_dict(orient='records'),
            'top_score': analysis_results.get('top_score', pd.DataFrame()).to_dict(orient='records'),
            'charts': charts,
            'portfolio': portfolio_advice,
            # 添加格式化函数
            'format_percentage': format_percentage,
            'format_currency': format_currency,
            'format_value': format_value
        }
        
        # 加载模板
        template = template_env.get_template('report_template.html')
        html_content = template.render(report_data)
        
        # 保存文件
        if output_file is None:
            output_file = f"reports/ETF市场日报_{datetime.now().strftime('%Y%m%d')}.html"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"已生成HTML报告：{output_file}")
        return html_content
    
    except Exception as e:
        logger.error(f"生成HTML报告失败: {str(e)}\n{traceback.format_exc()}")
        return "<h1>报告生成失败</h1>"
