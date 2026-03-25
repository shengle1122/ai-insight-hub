# 🤖 AI Insight Hub

智能资讯聚合平台 - 每日自动采集、分析、呈现三大领域核心资讯

[![Daily AI News](https://github.com/hzhuangkai/ai-insight-hub/actions/workflows/daily-ai-news.yml/badge.svg)](https://github.com/hzhuangkai/ai-insight-hub/actions/workflows/daily-ai-news.yml)
[![Daily HK Stock](https://github.com/hzhuangkai/ai-insight-hub/actions/workflows/daily-hk-stock.yml/badge.svg)](https://github.com/hzhuangkai/ai-insight-hub/actions/workflows/daily-hk-stock.yml)
[![Daily House Price](https://github.com/hzhuangkai/ai-insight-hub/actions/workflows/daily-house-price.yml/badge.svg)](https://github.com/hzhuangkai/ai-insight-hub/actions/workflows/daily-house-price.yml)
[![GitHub Pages](https://github.com/hzhuangkai/ai-insight-hub/actions/workflows/deploy-pages.yml/badge.svg)](https://hzhuangkai.github.io/ai-insight-hub/)

## 📋 功能模块

### 1. 🤖 AI行业动态
- **数据来源**: Hacker News, arXiv, GitHub Trending
- **更新频率**: 每日早8:00 (UTC+8)
- **内容**: AI新闻聚合、论文推荐、热门项目
- **特色**: LLM智能筛选，生成中文简报

### 2. 📈 港股行情分析
- **数据来源**: Yahoo Finance
- **更新频率**: 每日早8:00 (UTC+8)
- **内容**: 恒生指数、热门港股7日走势分析
- **特色**: 可视化图表、AI市场洞察

### 3. 🏠 房价趋势分析
- **数据来源**: 模拟数据（可接入链家/贝壳真实数据）
- **更新频率**: 每日早8:00 (UTC+8)
- **内容**: 重点城市房价、杭州各区深度分析
- **特色**: 区域对比、趋势预测

## 🚀 快速开始

### 1. Fork/Clone 项目

```bash
git clone https://github.com/hzhuangkai/ai-insight-hub.git
cd ai-insight-hub
```

### 2. 配置 GitHub Secrets

在仓库 Settings → Secrets → Actions 中添加：

- `OPENAI_API_KEY`: 你的OpenAI API密钥（用于AI简报生成）

### 3. 启用 GitHub Pages

Settings → Pages → Source: Deploy from a branch → Branch: main /docs

### 4. 运行测试

```bash
# 安装依赖
pip install -r requirements.txt

# 测试AI新闻模块
python src/modules/ai_news/collector.py
python src/modules/ai_news/generator.py

# 测试港股模块
python src/modules/hk_stock/collector.py
python src/modules/hk_stock/generator.py

# 测试房价模块
python src/modules/house_price/collector.py
python src/modules/house_price/generator.py
```

## 📁 项目结构

```
ai-insight-hub/
├── .github/workflows/          # GitHub Actions 工作流
│   ├── daily-ai-news.yml      # AI新闻定时任务
│   ├── daily-hk-stock.yml     # 港股分析定时任务
│   ├── daily-house-price.yml  # 房价分析定时任务
│   └── deploy-pages.yml       # GitHub Pages 部署
├── src/
│   └── modules/               # 各模块代码
│       ├── ai_news/           # AI新闻模块
│       ├── hk_stock/          # 港股模块
│       └── house_price/       # 房价模块
├── data/                      # 采集的数据(JSON)
├── docs/                      # GitHub Pages 站点
│   ├── index.html             # 首页
│   ├── ai-news-report.html    # AI新闻页面
│   ├── hk-stock-report.html   # 港股页面
│   └── house-price-report.html # 房价页面
├── requirements.txt           # Python依赖
└── README.md                  # 项目说明
```

## 🔧 自定义配置

### 修改定时时间

编辑 `.github/workflows/*.yml` 文件中的 cron 表达式：

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # UTC 00:00 = 北京时间 8:00
```

### 添加自定义数据源

在 `src/modules/<module>/collector.py` 中添加新的采集函数。

### 接入真实房价数据

修改 `src/modules/house_price/collector.py`：

1. 申请链家/贝壳API
2. 替换 `generate_mock_data()` 函数
3. 更新 `real_data_sources` 配置

## 📝 数据来源说明

| 模块 | 数据源 | 更新频率 |
|------|--------|----------|
| AI新闻 | Hacker News API, arXiv API, GitHub API | 实时 |
| 港股 | Yahoo Finance API | 15分钟延迟 |
| 房价 | 模拟数据/链家/贝壳 | 每日 |

## ⚠️ 免责声明

- 本项目的港股分析和房价数据仅供学习参考
- 不构成任何投资建议或购房建议
- 投资有风险，入市需谨慎

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

Made with ❤️ by GitHub Actions
