# 📈 股票数据统计系统

一个基于富途和同花顺API的股票数据统计系统，支持定时数据采集、数据库存储和Web界面查询。

## 🚀 功能特性

### 核心功能
- **定时数据采集**: 自动获取富途和同花顺的股票数据
- **智能数据存储**: 将统计数据存储到SQLite数据库
- **美观的Web界面**: 提供现代化的数据查询和展示界面
- **股票搜索**: 支持按股票代码或名称搜索历史数据
- **多维度统计**: 涨幅榜、成交量榜、成交额榜及交集分析

### 数据源
- **富途数据**: 大A市场和港股市场数据
- **同花顺数据**: A股市场数据

### 统计维度
- 成交额前10
- 涨幅前50  
- 成交量前50
- 涨幅与成交量交集

## 📋 系统要求

- Python 3.7+
- 富途牛牛客户端（用于富途API）
- 同花顺账户（用于同花顺API）

## 🛠 安装配置

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd futu-chat
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置富途
- 安装并启动富途牛牛客户端
- 在客户端中启用OpenAPI功能
- 确保API端口为11111（默认）

### 4. 配置同花顺
- 在 `ifind.py` 中配置你的同花顺refreshToken
- 确保token有效且有相应的数据权限

### 5. 配置微信推送（可选）
- 在 `wx_push.py` 中配置你的微信推送信息

## 🏃‍♂️ 运行系统

### 方式一：完整系统启动
```bash
python start_app.py
```
这将同时启动：
- 定时数据采集服务
- Web查询界面（访问 http://localhost:5000）

### 方式二：分别启动

#### 只运行定时任务
```bash
python schedule_stocks.py
```

#### 只运行Web界面
```bash
python web_app.py
```

## 🌐 Web界面使用

访问 `http://localhost:5000` 即可使用Web界面：

### 主要功能
1. **日期选择**: 选择要查询的统计日期
2. **数据源筛选**: 可选择查看富途或同花顺数据
3. **市场切换**: 支持A股和港股数据切换
4. **类型切换**: 在成交额、涨幅、成交量和交集间切换
5. **股票搜索**: 输入股票代码或名称进行搜索
6. **数据摘要**: 显示当日数据统计概览

### 界面特色
- 📱 响应式设计，支持移动端访问
- 🎨 现代化UI设计，美观易用
- ⚡ 快速数据加载和切换
- 🔍 强大的搜索功能
- 📊 直观的数据展示

## 📁 项目结构

```
futu-chat/
├── database.py          # 数据库操作模块
├── futu_data.py         # 富途数据获取模块
├── ifind.py             # 同花顺数据获取模块
├── schedule_stocks.py   # 定时任务模块
├── web_app.py           # Web应用模块
├── start_app.py         # 系统启动脚本
├── wx_push.py           # 微信推送模块
├── requirements.txt     # 依赖包列表
├── stock_data.db        # SQLite数据库文件（运行后生成）
├── stocks/              # 股票代码文件目录
│   ├── A_code.txt       # A股代码列表
│   └── stocks_HK.txt    # 港股代码列表
└── templates/           # Web模板目录
    └── index.html       # 主页模板
```

## ⏰ 定时任务说明

### 运行时间
- **工作日**: 周一至周五
- **时间段**: 09:00-16:00
- **频率**: 每小时的55分执行一次

### 执行逻辑
1. 获取富途数据（大A + 港股）
2. 获取同花顺数据（A股）
3. 保存数据到数据库
4. 发送微信推送通知

## 🗄 数据库说明

使用SQLite数据库存储统计数据：

### 表结构
- `stock_statistics`: 主数据表
  - `id`: 主键
  - `date`: 统计日期
  - `time`: 统计时间  
  - `data_source`: 数据源（futu/tonghuashun）
  - `market`: 市场（A/HK）
  - `data_type`: 数据类型（top_amount/top_change/top_volume/intersection）
  - `stock_data`: JSON格式的股票数据
  - `created_at`: 创建时间

### 数据查询
系统提供多种查询方式：
- 按日期查询
- 按数据源筛选
- 按股票代码/名称搜索
- 获取股票历史记录

## 🔧 自定义配置

### 修改采集频率
在 `schedule_stocks.py` 中修改：
```python
schedule.every().hour.at(":55").do(futu_job)  # 每小时55分执行
```

### 修改运行时间段
在 `schedule_stocks.py` 的main函数中修改：
```python
if 0 <= current_weekday <= 4 and 9 <= current_time.hour <= 16:  # 工作日9-16点
```

### 修改Web端口
在 `web_app.py` 或 `start_app.py` 中修改：
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # 修改port参数
```

## 📊 API接口

系统提供RESTful API接口：

- `GET /api/dates` - 获取可用日期列表
- `GET /api/statistics/<date>` - 获取指定日期统计数据
- `GET /api/stock_history/<stock_code>` - 获取股票历史记录
- `GET /api/summary/<date>` - 获取指定日期摘要
- `GET /api/search_stock?keyword=<keyword>` - 搜索股票

## 🚨 注意事项

1. **富途API限制**: 确保富途客户端运行且API已启用
2. **同花顺Token**: 定期更新refreshToken，避免过期
3. **数据准确性**: 数据仅供参考，投资需谨慎
4. **系统资源**: 长期运行请注意磁盘空间和内存使用
5. **网络环境**: 确保网络连接稳定，避免数据获取失败

## 🤝 贡献

欢迎提交Issue和Pull Request来改进本项目！

## 📄 许可证

本项目仅供学习和研究使用。
