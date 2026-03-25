#!/usr/bin/env python3
"""
港股行情分析报告生成器
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data/hk_stock")
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)


class HKStockGenerator:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data_file = DATA_DIR / f"{self.today}.json"
        self.report_file = DOCS_DIR / "hk-stock-report.md"
    
    def load_data(self):
        """加载数据"""
        if not self.data_file.exists():
            files = sorted(DATA_DIR.glob("*.json"), reverse=True)
            if files:
                self.data_file = files[0]
            else:
                raise FileNotFoundError("No stock data found")
        
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def generate_chart_data(self, data):
        """生成Chart.js图表数据"""
        charts = []
        
        for code, info in data.get("indices", {}).items():
            if "history" in info and len(info["history"]) >= 2:
                labels = [h["date"][5:] for h in info["history"]]  # 取 MM-DD
                values = [h["close"] for h in info["history"] if h["close"]]
                
                if values:
                    charts.append({
                        "code": code,
                        "name": info["name"],
                        "labels": labels,
                        "values": values,
                        "latest": info["latest"],
                        "change_pct": info["change_pct"]
                    })
        
        return charts
    
    def generate_report(self):
        """生成报告"""
        print(f"📄 Generating HK stock report for {self.today}...")
        
        data = self.load_data()
        charts = self.generate_chart_data(data)
        
        # 市场概览
        summary = data.get("market_summary", {})
        
        report = f"""# 📈 港股行情分析

**报告日期**: {datetime.now().strftime("%Y年%m月%d日")}  
**数据范围**: 近7日行情

---

## 📊 市场概览

| 指标 | 数值 |
|------|------|
| 上涨家数 | 🔴 {summary.get('up_count', 0)} |
| 下跌家数 | 🟢 {summary.get('down_count', 0)} |
| 平盘家数 | ⚪ {summary.get('flat_count', 0)} |

### 今日明星
- **涨幅最大**: {summary.get('top_gainer', {}).get('name', 'N/A')} ({summary.get('top_gainer', {}).get('change_pct', 0):+.2f}%)
- **跌幅最大**: {summary.get('top_loser', {}).get('name', 'N/A')} ({summary.get('top_loser', {}).get('change_pct', 0):+.2f}%)

---

## 📉 主要指数

"""
        # 指数详情
        for code, info in data.get("indices", {}).items():
            emoji = "📈" if info["change"] >= 0 else "📉"
            report += f"""### {emoji} {info['name']} ({code})

- **最新**: {info['latest']:.2f}
- **涨跌**: {info['change']:+.2f} ({info['change_pct']:+.2f}%)

"""
        
        report += """---

## 💼 热门个股

| 代码 | 名称 | 最新价 | 涨跌 | 涨跌幅 | 周高 | 周低 |
|------|------|--------|------|--------|------|------|
"""
        
        for symbol, info in data.get("stocks", {}).items():
            emoji = "🔴" if info["change"] >= 0 else "🟢"
            report += f"| {symbol} | {info['name']} | {info['latest']:.2f} | {emoji} {info['change']:+.2f} | {info['change_pct']:+.2f}% | {info['week_high']:.2f} | {info['week_low']:.2f} |\n"
        
        report += f"""

---

## 📈 7日走势图

*图表数据已生成，可在网页版查看交互式图表*

"""
        
        # 如果有LLM API，添加AI分析
        try:
            analysis = self.generate_ai_analysis(data)
            report += f"""## 🤖 AI分析

{analysis}

"""
        except Exception as e:
            print(f"AI analysis skipped: {e}")
        
        report += f"""---

*数据来源: Yahoo Finance | 更新时间: {datetime.now().strftime("%H:%M")}*

⚠️ **免责声明**: 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
"""
        
        # 保存报告
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✓ Report saved to {self.report_file}")
        
        # 同时生成JSON供前端使用
        self.save_json_data(data, charts)
        
        return report
    
    def generate_ai_analysis(self, data):
        """使用LLM生成分析"""
        try:
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "（AI分析功能未启用，请配置OPENAI_API_KEY）"
            
            client = openai.OpenAI(api_key=api_key)
            
            # 构建提示
            indices_info = []
            for code, info in data.get("indices", {}).items():
                indices_info.append(f"{info['name']}: {info['latest']:.2f} ({info['change_pct']:+.2f}%)")
            
            stocks_info = []
            for symbol, info in data.get("stocks", {}).items():
                stocks_info.append(f"{info['name']}: {info['latest']:.2f} ({info['change_pct']:+.2f}%)")
            
            prompt = f"""作为一位专业的港股分析师，请对以下今日港股行情进行简要分析：

**主要指数表现**:
{chr(10).join(indices_info)}

**热门个股表现**:
{chr(10).join(stocks_info[:5])}

请从以下几个方面进行分析（用中文，简洁专业）：
1. 市场整体情绪（牛市/熊市/震荡）
2. 主要驱动因素分析
3. 短期趋势判断
4. 风险提示

控制在300字以内。"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一位专业的港股分析师，擅长技术分析和市场判断。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"（AI分析生成失败: {e}）"
    
    def save_json_data(self, data, charts):
        """保存JSON数据供前端使用"""
        output = {
            "date": self.today,
            "indices": data.get("indices", {}),
            "stocks": data.get("stocks", {}),
            "market_summary": data.get("market_summary", {}),
            "charts": charts
        }
        
        json_file = DOCS_DIR / "hk-stock-data.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON data saved to {json_file}")
    
    def run(self):
        """运行生成流程"""
        self.generate_report()
        print("✓ Report generation complete!")


if __name__ == "__main__":
    generator = HKStockGenerator()
    generator.run()
