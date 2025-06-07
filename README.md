### 🤖 Assistant



# ETF市场日报生成系统

## 项目概述

ETF市场日报生成系统是一个自动化工具，用于分析ETF市场数据并生成专业级的日报报告。该系统结合了多种金融分析技术，包括多因子模型、动量分析和价值投资策略，为投资者提供全面的市场洞察和投资建议。

![系统架构图](https://via.placeholder.com/800x400.png?text=ETF+Report+System+Architecture)

## 功能特点

1. **全面数据分析**
   - 实时计算ETF涨跌幅、成交额、换手率等关键指标
   - 多因子综合评分系统（动量、价值、流动性等）
   - 溢折率分析和折价机会识别
   - 自动异常值检测与筛选

2. **智能投资组合建议**
   - 多种投资策略支持（成长型、价值型、动量型、平衡型）
   - 行业分散投资组合构建
   - 组合风险评估和预期收益计算
   - 智能权重分配算法

3. **专业报告生成**
   - 支持Markdown和HTML格式输出
   - 嵌入式可视化图表（基于matplotlib和plotly）
   - 微信公众号友好格式
   - 可定制报告模板

4. **高度可配置**
   - 模块化设计，易于扩展
   - 权重参数和阈值可配置
   - 自定义报告模板
   - 超时保护机制

## 安装指南

### 前置要求

- Python 3.8+
- pip包管理工具

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/etf-daily-report.git
   cd etf-daily-report
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 准备数据：
   - 将您的ETF数据文件放入`data/`目录
   - 支持的格式：CSV（.csv）和Excel（.xlsx, .xls）
   - 默认文件名为`ETF行情数据.csv`或`ETF行情数据.xlsx`

## 数据格式要求

系统支持以下两种格式的ETF数据：

1. **CSV格式**：UTF-8编码的CSV文件
2. **Excel格式**：.xlsx或.xls文件

数据文件必须包含以下字段：
- 代码
- 名称
- 最新价
- 涨跌幅
- 成交额
- 换手率
- 市盈率
- 溢价率（可选）

## 使用说明

### 数据文件检查

在运行主程序前，可以先检查数据文件是否可用：

```bash
# 检查并列出可用的数据文件
python check_data_file.py --list
```

### 基本使用

```bash
# 生成Markdown报告（默认）
python main.py

# 指定数据文件
python main.py data/ETF行情数据.csv

# 生成HTML报告
python main.py --format html --output reports/etf_report.html
```

### 高级选项

```bash
# 自定义输出路径
python main.py --output custom_reports/daily_report.md

# 使用Windows批处理文件（简化命令）
run.bat
```

### 运行参数说明

| 参数 | 短格式 | 说明 | 默认值 |
|------|--------|------|--------|
| `data_file` | - | ETF数据文件路径 | `data/ETF行情数据.csv` |
| `--output` | `-o` | 输出文件路径 | 自动生成（基于当前日期） |
| `--format` | `-f` | 报告格式：md或html | `md` |

### 配置文件

系统提供三个主要配置文件：

1. `configs/analysis_config.py` - 分析参数配置
   ```python
   # 分析权重配置
   ANALYSIS_WEIGHTS = {
       '涨跌幅': 0.15,
       '5日涨跌幅': 0.20,
       # ...其他权重
   }
   ```

2. `configs/portfolio_config.py` - 投资组合配置
   ```python
   # 投资组合类别
   PORTFOLIO_CATEGORIES = {
       '科技类': ['科技', '互联网', '5G'],
       # ...其他类别
   }
   ```

3. `configs/report_config.py` - 报告生成配置
   ```python
   # 报告章节配置
   REPORT_CONFIG = {
       'sections': [
           'market_overview',
           'performance_ranking',
           # ...其他章节
       ]
   }
   ```

## 项目结构

```
etf-daily-report/
├── configs/                  # 配置文件
│   ├── analysis_config.py    # 分析参数
│   ├── portfolio_config.py   # 组合配置
│   └── report_config.py      # 报告配置
├── data/                     # 数据目录
│   ├── ETF行情数据.csv       # CSV格式数据
│   └── ETF行情数据.xlsx      # Excel格式数据
├── modules/                  # 核心模块
│   ├── data_loader.py        # 数据加载
│   ├── analyzer.py           # 数据分析
│   ├── visualizer.py         # 可视化
│   ├── portfolio_builder.py  # 组合构建
│   └── report_generator.py   # 报告生成
├── templates/                # 报告模板
│   └── report_template.html  # HTML模板
├── utils/                    # 工具函数
│   ├── helpers.py            # 辅助工具
│   └── logging_config.py     # 日志配置
├── reports/                  # 生成的报告
├── logs/                     # 日志文件
├── main.py                   # 主程序入口
├── check_data_file.py        # 数据文件检查工具
├── run.bat                   # Windows运行脚本
├── requirements.txt          # Python依赖
└── README.md                 # 项目文档
```

## 依赖说明

项目使用以下主要Python库：

```
pandas>=2.1.4     # 数据处理
numpy>=1.26.4     # 数学计算
chardet>=5.2.0    # 字符编码检测
openpyxl>=3.1.2   # Excel文件支持
matplotlib>=3.8.2 # 基础图表生成
scipy>=1.12.0     # 科学计算
jinja2>=3.1.3     # 模板渲染
plotly>=5.20.0    # 交互式图表
kaleido>=0.2.1    # 静态图表导出
```

## 报告示例

### 市场概览
```
今日市场共有256只ETF交易，158只上涨，78只下跌，20只平盘，平均涨幅0.82%。
成交额最高的ETF为沪深300ETF（510300），成交额达56.2亿元。
```

### 投资组合建议
| 类别       | ETF名称           | 代码       | 现价   | 综合得分 |
|------------|-------------------|------------|--------|----------|
| 科技类     | 科技龙头ETF       | 515000.SH  | 1.235  | 8.72     |
| 金融类     | 银行ETF           | 512800.SH  | 1.102  | 7.85     |
| 医药类     | 医疗创新ETF       | 516820.SH  | 0.893  | 7.63     |

### 风险提示
```
过去表现不代表未来，投资需谨慎。市场波动可能导致短期亏损。
本报告不构成投资建议，仅供参考。
```

## 性能说明

系统处理约1000只ETF数据的典型运行时间：
- 数据加载：< 1秒
- 数据分析：~2秒
- 图表生成：~10秒
- 报告生成：~3秒
- 总运行时间：约15-20秒

系统包含超时保护机制，默认超时时间为5分钟。

## 定制化开发

### 修改分析参数
编辑`configs/analysis_config.py`：
```python
# 调整权重分配
ANALYSIS_WEIGHTS = {
    '涨跌幅': 0.20,  # 增加当日涨幅权重
    '5日涨跌幅': 0.15,
    # ...
}
```

### 自定义投资组合
编辑`configs/portfolio_config.py`：
```python
# 添加新的投资类别
PORTFOLIO_CATEGORIES = {
    '新能源': ['新能源', '光伏', '锂电池'],
    # ...其他类别
}
```

### 修改报告模板
编辑`templates/report_template.html`：
```html
<!-- 添加自定义章节 -->
<section class="custom-section">
  <h2>我的自定义分析</h2>
  <p>{{ custom_content }}</p>
</section>
```

## 常见问题

1. **Q: 数据文件无法加载怎么办？**  
   A: 请检查文件编码（应为UTF-8）和格式，确保必要字段存在。运行`check_data_file.py`可以帮助诊断问题。

2. **Q: 报告生成超时？**  
   A: 检查数据文件大小，如果过大可能导致处理延迟。尝试减少数据量或修改`main.py`中的超时设置。

3. **Q: 如何添加自定义分析指标？**  
   A: 在`modules/analyzer.py`中添加新的分析函数，并在`configs/analysis_config.py`中配置相应的权重。

## 贡献指南

我们欢迎贡献！请遵循以下步骤：

1. Fork项目仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起Pull Request

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 技术支持

如有任何问题或建议，请联系：
- 邮箱：support@etfreport.com
- GitHub Issues: [https://github.com/yourusername/etf-daily-report/issues]()

```
投资有风险，入市需谨慎。本系统生成的分析报告仅供参考，不构成任何投资建议。
```

