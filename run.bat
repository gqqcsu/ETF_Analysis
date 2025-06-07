@echo off
echo 开始生成ETF市场日报...
python main.py data/ETF行情数据.csv --output reports/ETF日报.html --format html
echo 日报已生成: reports/ETF日报.html
pause
