import pandas as pd
import numpy as np
from configs.portfolio_config import PORTFOLIO_CATEGORIES, PORTFOLIO_WEIGHTS
from configs.analysis_config import ANALYSIS_WEIGHTS
from .analyzer import calculate_composite_score
import logging
from utils.logging_config import logger

def build_category_portfolio(df, category, n=2):
    """
    构建特定类别的投资组合
    
    参数:
    df: 包含ETF数据的DataFrame
    category: 要构建的类别名称（如'科技类'、'金融类'等）
    n: 每个类别选择的ETF数量
    
    返回:
    包含该类别推荐ETF的DataFrame
    """
    try:
        keywords = PORTFOLIO_CATEGORIES.get(category, [])
        if not keywords:
            return pd.DataFrame()
        
        # 根据关键词筛选
        mask = pd.Series(False, index=df.index)
        for kw in keywords:
            mask |= df['名称'].str.contains(kw, na=False)
        
        if mask.sum() == 0:
            return pd.DataFrame()
        
        category_df = df[mask].copy()
        
        # 确保有综合得分
        if '综合得分' not in category_df.columns:
            category_df['综合得分'] = calculate_composite_score(category_df)
        
        return category_df.nlargest(n, '综合得分')
    
    except Exception as e:
        logger.error(f"构建类别组合[{category}]失败: {str(e)}")
        return pd.DataFrame()

def build_strategy_portfolio(df, strategy='balanced', top_n=5):
    """
    根据特定策略构建投资组合
    
    参数:
    df: 包含ETF数据的DataFrame
    strategy: 投资策略（'growth'成长型, 'value'价值型, 'momentum'动量型, 'balanced'平衡型）
    top_n: 选择的ETF数量
    
    返回:
    包含策略推荐ETF的DataFrame
    """
    try:
        # 确保有综合得分
        if '综合得分' not in df.columns:
            df['综合得分'] = calculate_composite_score(df)
        
        if strategy == 'growth':
            # 成长型策略：选择年初至今表现最好的ETF
            return df.nlargest(top_n, '年初至今')
        
        elif strategy == 'value':
            # 价值型策略：选择低估值ETF
            if '市盈率' in df.columns and '市净率' in df.columns:
                # 只考虑有完整估值数据的ETF
                value_df = df[(df['市盈率'] > 0) & (df['市净率'] > 0)].copy()
                value_df['估值得分'] = value_df['市盈率'] * 0.6 + value_df['市净率'] * 0.4
                return value_df.nsmallest(top_n, '估值得分')
            else:
                return df.nlargest(top_n, '综合得分')
        
        elif strategy == 'momentum':
            # 动量型策略：选择动量得分最高的ETF
            if '动量得分' not in df.columns:
                df['动量得分'] = 0.3 * df['涨跌幅'] + 0.7 * df['5日涨跌幅']
            return df.nlargest(top_n, '动量得分')
        
        else:  # balanced 平衡型策略
            return df.nlargest(top_n, '综合得分')
    
    except Exception as e:
        logger.error(f"构建策略组合[{strategy}]失败: {str(e)}")
        return df.head(top_n)  # 返回默认值

def build_diversified_portfolio(df):
    """
    构建分散投资组合，包含不同类型的ETF
    
    参数:
    df: 包含ETF数据的DataFrame
    
    返回:
    字典，包含每个类别的推荐ETF
    """
    portfolio = {}
    
    try:
        # 确保有综合得分
        if '综合得分' not in df.columns:
            df['综合得分'] = calculate_composite_score(df)
        
        # 选择不同类型的ETF
        for category, keywords in PORTFOLIO_CATEGORIES.items():
            # 创建筛选条件
            mask = pd.Series(False, index=df.index)
            for kw in keywords:
                mask |= df['名称'].str.contains(kw, na=False)
            
            if mask.sum() > 0:
                category_df = df[mask]
                portfolio[category] = category_df.nlargest(2, '综合得分')
            else:
                # 如果没有符合条件的ETF，选择综合得分最高的ETF
                portfolio[category] = df.nlargest(2, '综合得分')
        
        return portfolio
    
    except Exception as e:
        logger.error(f"构建分散组合失败: {str(e)}")
        return {}

def calculate_portfolio_metrics(portfolio, strategy):
    """
    计算投资组合的预期收益和风险指标
    
    参数:
    portfolio: 投资组合数据（DataFrame或字典）
    strategy: 投资策略名称（用于确定权重）
    
    返回:
    包含指标和权重的字典
    """
    try:
        # 如果portfolio是DataFrame，转换为列表形式
        if isinstance(portfolio, pd.DataFrame):
            portfolio_list = [portfolio]
        elif isinstance(portfolio, dict):
            portfolio_list = list(portfolio.values())
        else:
            raise ValueError("不支持的portfolio数据类型")
        
        # 获取配置的权重
        default_weight = 1.0 / len(portfolio_list)  # 默认等权重
        weights = PORTFOLIO_WEIGHTS.get(strategy, [default_weight] * len(portfolio_list))
        
        # 处理权重和投资组合长度不匹配的情况
        if len(weights) < len(portfolio_list):
            # 如果配置的权重数量少于组合数量，使用默认等权重
            logger.warning(f"策略[{strategy}]的权重数量({len(weights)})少于组合数量({len(portfolio_list)})，使用等权重")
            weights = [default_weight] * len(portfolio_list)
        elif len(weights) > len(portfolio_list):
            # 如果配置的权重数量多于组合数量，截断多余的权重
            logger.warning(f"策略[{strategy}]的权重数量({len(weights)})多于组合数量({len(portfolio_list)})，截断多余权重")
            weights = weights[:len(portfolio_list)]
        
        # 确保权重总和为1
        weights = np.array(weights)
        if np.sum(weights) != 0:
            weights = weights / np.sum(weights)
        
        # 计算预期收益（使用年初至今收益作为代理）
        returns = []
        valid_etfs = 0
        
        for etf_df in portfolio_list:
            if not etf_df.empty:
                if '年初至今' in etf_df.columns and not pd.isna(etf_df['年初至今'].iloc[0]):
                    returns.append(etf_df['年初至今'].iloc[0])
                    valid_etfs += 1
                elif '5日涨跌幅' in etf_df.columns and not pd.isna(etf_df['5日涨跌幅'].iloc[0]):
                    returns.append(etf_df['5日涨跌幅'].iloc[0])
                    valid_etfs += 1
                else:
                    returns.append(0)
        
        # 如果没有有效ETF，返回默认值
        if valid_etfs == 0:
            return {
                '预期收益率': 0,
                '风险等级': "未知",
                'weights': weights.tolist()
            }
        
        # 确保returns和weights长度一致
        if len(returns) != len(weights):
            # 调整returns长度与weights一致
            if len(returns) < len(weights):
                returns = returns + [0] * (len(weights) - len(returns))
            else:
                returns = returns[:len(weights)]
        
        # 计算加权预期收益率
        weighted_return = np.sum(np.array(returns) * weights)
        
        # 风险评估
        if weighted_return > 0.2:
            risk_level = "高"
        elif weighted_return < 0.05:
            risk_level = "低"
        else:
            risk_level = "中等"
        
        return {
            '预期收益率': weighted_return,
            '风险等级': risk_level,
            'weights': weights.tolist()
        }
    
    except Exception as e:
        logger.error(f"计算投资组合指标时出错: {str(e)}")
        return {
            '预期收益率': 0,
            '风险等级': "未知",
            'weights': [1/len(portfolio_list)] * len(portfolio_list)  # 等权重
        }

def generate_portfolio_advice(df):
    """
    生成完整的投资组合建议
    
    参数:
    df: 包含ETF数据的DataFrame
    
    返回:
    包含各类别和策略投资组合建议的字典
    """
    portfolio_advice = {}
    
    try:
        # 按行业类别构建组合
        for category in PORTFOLIO_CATEGORIES.keys():
            portfolio_advice[category] = build_category_portfolio(df, category, 2)
        
        # 构建策略组合
        strategies = ['growth', 'value', 'momentum', 'balanced']
        for strategy in strategies:
            portfolio_advice[strategy] = build_strategy_portfolio(df, strategy, 5)
        
        # 构建分散组合
        portfolio_advice['diversified'] = build_diversified_portfolio(df)
        
        # 计算每个组合的指标 - 修复了迭代修改字典的问题
        # 创建临时字典存储指标
        metrics = {}
        
        for key in list(portfolio_advice.keys()):  # 使用keys的副本进行迭代
            if key in strategies:
                metrics[key + '_metrics'] = calculate_portfolio_metrics(
                    portfolio_advice[key], key)
            elif key == 'diversified':
                metrics['diversified_metrics'] = calculate_portfolio_metrics(
                    portfolio_advice['diversified'], 'diversified')
        
        # 将指标添加到主字典
        portfolio_advice.update(metrics)
        
        return portfolio_advice
    
    except Exception as e:
        logger.error(f"生成投资组合建议失败: {str(e)}")
        return {}
