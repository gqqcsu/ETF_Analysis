import argparse
import sys
import time
import matplotlib.pyplot as plt
from modules.data_loader import load_etf_data
from modules.analyzer import analyze_etf_data
from modules.visualizer import generate_all_charts
from modules.portfolio_builder import generate_portfolio_advice
from modules.report_generator import generate_markdown_report, generate_html_report
from utils.logging_config import logger
import traceback
import platform
import multiprocessing

def run_with_timeout(func, args=(), timeout=120):
    """使用多进程实现超时功能"""
    pool = multiprocessing.Pool(processes=1)
    try:
        result = pool.apply_async(func, args)
        return result.get(timeout=timeout)
    except multiprocessing.TimeoutError:
        logger.error("操作超时")
        return None
    except Exception as e:
        logger.error(f"执行过程中发生错误: {str(e)}")
        return None
    finally:
        pool.close()
        pool.terminate()

def main_process(data_file, output_file, report_type):
    """在单独进程中运行的主逻辑"""
    try:
        # 1. 加载数据
        logger.info("正在加载ETF数据...")
        df = load_etf_data(data_file)
        if df is None or df.empty:
            logger.error("加载的数据为空，请检查数据文件")
            return "数据加载失败"
        
        logger.info(f"成功加载 {len(df)} 条ETF数据")
        
        # 2. 数据分析
        logger.info("正在分析ETF数据...")
        start_analysis = time.time()
        analysis_results = analyze_etf_data(df)
        logger.info(f"数据分析完成，耗时: {time.time() - start_analysis:.2f}秒")
        
        # 3. 生成图表
        logger.info("正在生成可视化图表...")
        start_charts = time.time()
        charts = generate_all_charts(df, analysis_results)
        logger.info(f"图表生成完成，耗时: {time.time() - start_charts:.2f}秒")
        
        # 4. 生成投资组合建议
        logger.info("正在生成投资组合建议...")
        start_portfolio = time.time()
        portfolio_advice = generate_portfolio_advice(df)
        logger.info(f"投资组合生成完成，耗时: {time.time() - start_portfolio:.2f}秒")
        
        # 5. 生成报告
        logger.info("正在生成报告...")
        start_report = time.time()
        
        if report_type.lower() == 'html':
            report_content = generate_html_report(analysis_results, charts, portfolio_advice, output_file)
        else:
            report_content = generate_markdown_report(analysis_results, charts, portfolio_advice, output_file)
        
        logger.info(f"报告生成完成，耗时: {time.time() - start_report:.2f}秒")
        logger.info("报告生成完成！")
        
        return report_content
        
    except Exception as e:
        logger.error(f"报告生成失败: {str(e)}\n{traceback.format_exc()}")
        return "报告生成失败"
    finally:
        # 确保关闭所有matplotlib图形
        plt.close('all')

def main(data_file='data/ETF行情数据.csv', output_file=None, report_type='md'):
    """主函数入口，处理超时逻辑"""
    try:
        # 在Windows上使用多进程实现超时
        logger.info("使用多进程超时机制")
        
        # 设置超时时间（秒）
        timeout = 300  # 5分钟
        
        # 运行主逻辑并设置超时
        result = run_with_timeout(
            main_process, 
            args=(data_file, output_file, report_type), 
            timeout=timeout
        )
        
        if result is None:
            return "操作超时或执行失败"
        return result
        
    except Exception as e:
        logger.error(f"主函数错误: {str(e)}\n{traceback.format_exc()}")
        return "程序执行失败"
    finally:
        # 确保关闭所有matplotlib图形
        plt.close('all')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ETF市场日报生成工具')
    parser.add_argument('data_file', nargs='?', default='data/ETF行情数据.csv', help='ETF数据文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['md', 'html'], default='md', help='报告格式: md (Markdown) 或 html')
    
    args = parser.parse_args()
    result = main(args.data_file, args.output, args.format)
    
    if isinstance(result, str) and result.startswith("程序执行失败"):
        sys.exit(1)
