# 赛狐ERP数据同步项目

## 项目简介
本项目用于定时（每4小时）同步赛狐ERP的产品分析数据和FBA库存数据到本地数据库（SQLite），并提供本地测试脚本用于无API时的数据插入和更新。

## 主要依赖
- requests
- schedule
- sqlalchemy

## 使用说明
1. 安装依赖：
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. 启动定时同步：
   ```bash
   python main.py
   ```
3. 本地测试：
   ```bash
   python test_data.py
   ```

## 目录结构
- main.py         # 主同步逻辑
- db.py           # 数据库模型与操作
- test_data.py    # 本地测试脚本（插入/更新数据）
- requirements.txt
- README.md 