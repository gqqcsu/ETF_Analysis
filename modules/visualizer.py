import base64
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import platform
from io import BytesIO
import plotly.express as px
from configs.report_config import REPORT_CONFIG
import matplotlib as mpl
import time
import logging
from utils.logging_config import logger

# 设置中文字体
def set_chinese_font():
    """设置中文字体，避免乱码"""
    system = platform.system()
    try:
        if system == 'Windows':
            # 使用Windows系统默认中文字体
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong']
        elif system == 'Darwin':  # macOS
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC']
        else:  # Linux系统
            plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC']
        
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    except Exception as e:
        logger.error(f"设置中文字体失败: {str(e)}")

def fig_to_base64(fig, format='png', dpi=100):
    """将matplotlib图表转为base64编码"""
    try:
        img = BytesIO()
        fig.savefig(img, format=format, bbox_inches='tight', dpi=dpi, 
                   facecolor='white', edgecolor='none')
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode('utf-8')
    except Exception as e:
        logger.error(f"图表转换失败: {str(e)}")
        return ""
    finally:
        plt.close(fig)  # 关闭图表以释放资源

def create_histogram(data, column='涨跌幅', title='涨跌幅分布', bins=50):
    """创建直方图"""
    try:
        set_chinese_font()
        fig, ax = plt.subplots(figsize=REPORT_CONFIG['chart_sizes']['histogram'])
        ax.hist(data[column], bins=bins, alpha=0.7, color='skyblue')
        ax.set_title(title, fontsize=12)
        ax.set_xlabel(column, fontsize=10)
        ax.set_ylabel('数量', fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.7)
        return fig_to_base64(fig)
    except Exception as e:
        logger.error(f"创建直方图失败: {str(e)}")
        return ""

def create_bar_chart(series, title='', xlabel='', ylabel=''):
    """创建条形图"""
    try:
        set_chinese_font()
        fig, ax = plt.subplots(figsize=REPORT_CONFIG['chart_sizes']['bar_chart'])
        series.head(10).plot(kind='bar', ax=ax, color='lightblue')
        ax.set_title(title, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xlabel(xlabel, fontsize=10)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=8)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        return fig_to_base64(fig)
    except Exception as e:
        logger.error(f"创建条形图失败: {str(e)}")
        return ""

def create_pie_chart(series, title='', autopct='%1.1f%%'):
    """创建饼图"""
    try:
        set_chinese_font()
        fig, ax = plt.subplots(figsize=REPORT_CONFIG['chart_sizes']['pie_chart'])
        
        # 确保数据有效
        if series.isna().any() or (series == 0).all():
            logger.warning(f"无效的饼图数据: {series}")
            return ""
            
        series = series / series.sum() * 100
        wedges, texts, autotexts = ax.pie(series, 
                                         labels=series.index, 
                                         autopct=autopct,
                                         startangle=90,
                                         wedgeprops=dict(width=0.4, edgecolor='w'),
                                         pctdistance=0.85)
        
        ax.set_title(title, fontsize=12)
        ax.axis('equal')
        
        # 设置文本属性
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color('white')
        
        plt.tight_layout()
        return fig_to_base64(fig)
    except Exception as e:
        logger.error(f"创建饼图失败: {str(e)}")
        return ""

def create_scatter_plot(df, x_col, y_col, title='', xlabel='', ylabel=''):
    """创建美观的ETF综合得分 vs 成交额散点图"""
    try:
        set_chinese_font()
        
        # 过滤无效数据
        valid_data = df.dropna(subset=[x_col, y_col])
        if valid_data.empty:
            logger.warning(f"没有有效数据创建散点图: {x_col} vs {y_col}")
            return ""
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 设置样式 - 不使用预定义样式，直接设置属性
        # plt.style.use('seaborn')  # 使用seaborn样式
        plt.rcParams['axes.facecolor'] = '#f8f9fa'
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.linestyle'] = '--'
        
        # 使用颜色渐变表示综合得分
        scores = valid_data.get('综合得分', valid_data[y_col])
        norm = plt.Normalize(scores.min(), scores.max())
        cmap = plt.cm.get_cmap('viridis')
        
        # 绘制散点图
        scatter = ax.scatter(
            valid_data[x_col], 
            valid_data[y_col],
            c=scores,
            cmap=cmap,
            norm=norm,
            s=150,  # 点的大小
            alpha=0.8,
            edgecolors='w',
            linewidths=0.8
        )
        
        # 添加颜色条
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('综合得分', fontsize=12)
        
        # 添加趋势线 - 改进的方法，更稳定
        if len(valid_data) > 3:  # 确保有足够的数据点
            try:
                # 排除可能的异常值
                x_values = valid_data[x_col].values
                y_values = valid_data[y_col].values
                
                # 计算基本统计信息
                x_mean, x_std = np.mean(x_values), np.std(x_values)
                y_mean, y_std = np.mean(y_values), np.std(y_values)
                
                # 排除极端异常值 (超过3个标准差)
                if x_std > 0 and y_std > 0:  # 避免除以零
                    mask = (np.abs(x_values - x_mean) < 3 * x_std) & (np.abs(y_values - y_mean) < 3 * y_std)
                    filtered_x = x_values[mask]
                    filtered_y = y_values[mask]
                    
                    if len(filtered_x) > 2:  # 确保仍有足够的点
                        # 使用更稳定的拟合方法
                        with np.errstate(invalid='ignore'):  # 忽略警告
                            z = np.polyfit(filtered_x, filtered_y, 1)
                            p = np.poly1d(z)
                            
                            # 仅绘制在数据范围内的趋势线
                            x_min, x_max = np.min(filtered_x), np.max(filtered_x)
                            x_fit = np.linspace(x_min, x_max, 100)
                            plt.plot(x_fit, p(x_fit), "r--", linewidth=1.5, alpha=0.7)
                            
                            # 可选：添加R²值
                            # y_fit = p(filtered_x)
                            # r2 = 1 - (np.sum((filtered_y - y_fit)**2) / np.sum((filtered_y - np.mean(filtered_y))**2))
                            # plt.figtext(0.15, 0.05, f"R² = {r2:.3f}", fontsize=10, ha='left')
            except Exception as e:
                logger.warning(f"趋势线拟合失败: {str(e)}")
                # 如果高级拟合失败，不显示趋势线
        
        # 设置标题和标签
        ax.set_title(title or f'{y_col} vs {x_col}', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel or x_col, fontsize=12, labelpad=10)
        ax.set_ylabel(ylabel or y_col, fontsize=12, labelpad=10)
        
        # 格式化坐标轴
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x/100000000:,.1f}亿"))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, loc: f"{y:.2f}"))
        
        # 添加网格
        ax.grid(True, linestyle='--', alpha=0.7)  # 直接添加网格
        
        # 添加数据标签（只添加前10个，避免重叠）
        top_data = valid_data.sort_values(by=y_col, ascending=False).head(10)
        for i, row in top_data.iterrows():
            # 在点上方添加标签
            ax.annotate(row['名称'], 
                        (row[x_col], row[y_col]),
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center',
                        fontsize=9,
                        alpha=0.9,
                        bbox=dict(boxstyle="round,pad=0.3", 
                                  fc=(0.9, 0.9, 0.9, 0.7), 
                                  ec="grey", 
                                  lw=0.5))
        
        # 添加数据源说明
        plt.figtext(0.95, 0.01, "数据来源: ETF市场数据", 
                   fontsize=9, ha='right', alpha=0.7)
        
        plt.tight_layout()
        return fig_to_base64(fig, dpi=120)  # 使用更高的DPI提高清晰度
    
    except Exception as e:
        logger.error(f"创建散点图失败: {str(e)}")
        return ""


def generate_all_charts(df, analysis_results):
    """生成所有图表"""
    charts = {}
    logger.info("开始生成图表...")
    start_time = time.time()
    
    try:
        # 1. 涨跌幅分布图
        logger.info("生成涨跌幅分布图...")
        if not df.empty and '涨跌幅' in df.columns:
            charts['price_change_dist'] = create_histogram(df, '涨跌幅', 'ETF涨跌幅分布')
        
        # 2. 类型平均涨跌幅图
        logger.info("生成类型平均涨跌幅图...")
        if 'type_perf' in analysis_results and not analysis_results['type_perf'].empty:
            charts['type_performance'] = create_bar_chart(
                analysis_results['type_perf']['平均涨跌幅'], 
                '不同类型ETF平均涨跌幅', 
                'ETF类型', 
                '平均涨跌幅'
            )
        
        # 3. 成交额TOP10饼图
        logger.info("生成成交额TOP10饼图...")
        if 'top_volume' in analysis_results and not analysis_results['top_volume'].empty:
            top_volume = analysis_results['top_volume'].set_index('名称')['成交额']
            charts['volume_dist'] = create_pie_chart(top_volume, '成交额TOP10 ETF占比')
        
        # 4. 综合评分散点图 - 使用静态图表替代Plotly
        logger.info("生成综合评分散点图...")
        if '综合得分' in df.columns and not df.empty:
            charts['score_scatter'] = create_scatter_plot(
                df.head(30),
                '成交额',
                '综合得分',
                title='ETF综合得分 vs 成交额',
                xlabel='成交额',
                ylabel='综合得分'
            )
        
        # 记录图表生成时间
        elapsed = time.time() - start_time
        logger.info(f"图表生成完成，耗时: {elapsed:.2f}秒")
        return charts
    
    except Exception as e:
        logger.error(f"生成图表过程中出错: {str(e)}")
        return {}
