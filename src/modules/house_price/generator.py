#!/usr/bin/env python3
"""
房价趋势分析报告生成器
"""

import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data/house_price")
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)


class HousePriceGenerator:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data_file = DATA_DIR / f"{self.today}.json"
        self.report_file = DOCS_DIR / "house-price-report.md"
    
    def load_data(self):
        """加载数据"""
        if not self.data_file.exists():
            files = sorted(DATA_DIR.glob("*.json"), reverse=True)
            if files:
                self.data_file = files[0]
            else:
                raise FileNotFoundError("No house price data found")
        
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def generate_report(self):
        """生成报告"""
        print(f"📄 Generating house price report for {self.today}...")
        
        data = self.load_data()
        
        report = f"""# 🏠 房价趋势分析报告

**报告日期**: {datetime.now().strftime("%Y年%m月%d日")}

---

## 📊 重点城市房价概览

| 城市 | 等级 | 均价(元/㎡) | 月涨跌 | 趋势 |
|------|------|-------------|--------|------|
"""
        
        # 按等级和价格排序
        sorted_cities = sorted(
            data.get("cities", {}).items(),
            key=lambda x: x[1].get("avg_price", 0),
            reverse=True
        )
        
        for city_code, info in sorted_cities:
            emoji = "📈" if info.get("month_change_pct", 0) >= 0 else "📉"
            report += f"| {info['name']} | {info['tier']} | {info['avg_price']:,.0f} | {emoji} {info['month_change_pct']:+.2f}% | {self.get_trend_emoji(info['month_change_pct'])} |\n"
        
        # 杭州详细分析
        report += f"""

---

## 🏙️ 杭州楼市深度分析

### 各区均价对比

| 区域 | 均价(元/㎡) | 月涨跌 | 相对全市 |
|------|-------------|--------|----------|
"""
        
        hangzhou_avg = data.get("cities", {}).get("hangzhou", {}).get("avg_price", 32000)
        
        sorted_districts = sorted(
            data.get("hangzhou_detail", {}).items(),
            key=lambda x: x[1].get("avg_price", 0),
            reverse=True
        )
        
        for district_code, info in sorted_districts:
            emoji = "📈" if info.get("month_change_pct", 0) >= 0 else "📉"
            relative = (info.get("avg_price", 0) / hangzhou_avg - 1) * 100
            relative_str = f"+{relative:.1f}%" if relative >= 0 else f"{relative:.1f}%"
            report += f"| {info['name']} | {info['avg_price']:,.0f} | {emoji} {info['month_change_pct']:+.2f}% | {relative_str} |\n"
        
        report += f"""

### 杭州7日走势

"""
        
        # 添加走势图数据
        for district_code, info in list(data.get("hangzhou_detail", {}).items())[:4]:
            report += f"**{info['name']}**: "
            for day in info.get("trend", []):
                report += f"{day['date'][5:]} ¥{day['price']:,.0f} ({day['change_pct']:+.2f}%) → "
            report = report.rstrip(" → ") + "\n\n"
        
        # 分析总结
        report += """---

## 💡 市场洞察

### 核心观点

1. **整体趋势**
   - 一线城市价格保持稳定，波动较小
   - 新一线城市呈现分化态势
   - 杭州作为新一线龙头，表现相对稳健

2. **杭州市场特点**
   - 核心城区（西湖、滨江）价格坚挺
   - 周边城区（萧山、余杭）价格相对亲民
   - 未来科技城等新兴板块值得关注

3. **投资建议**
   - 刚需购房：可关注余杭、萧山等新兴区域
   - 改善型购房：西湖、滨江等核心区域保值性强
   - 投资需谨慎，关注政策动向

---

## 📚 数据来源说明

"""
        
        if data.get("data_source"):
            report += f"**当前数据来源**: {data['data_source']}\n\n"
        
        report += """**推荐真实数据源**:

| 平台 | 接入方式 | 更新频率 |
|------|----------|----------|
| 链家 | API申请/爬虫 | 日更 |
| 贝壳找房 | API申请 | 日更 |
| 安居客 | 数据合作 | 周更 |
| 国家统计局 | 官方API | 月度 |

---

⚠️ **免责声明**: 本报告数据仅供演示参考，不构成购房或投资建议。实际房价请以官方数据为准。

*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
        
        # 保存报告
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✓ Report saved to {self.report_file}")
        
        # 保存JSON供前端使用
        self.save_json_data(data)
        
        return report
    
    def get_trend_emoji(self, change_pct):
        """根据涨跌幅返回趋势表情"""
        if change_pct > 1:
            return "📈📈 大涨"
        elif change_pct > 0:
            return "📈 上涨"
        elif change_pct > -1:
            return "📉 下跌"
        else:
            return "📉📉 大跌"
    
    def save_json_data(self, data):
        """保存JSON数据供前端使用"""
        output = {
            "date": self.today,
            "cities": data.get("cities", {}),
            "hangzhou_detail": data.get("hangzhou_detail", {}),
            "data_source": data.get("data_source", "")
        }
        
        json_file = DOCS_DIR / "house-price-data.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON data saved to {json_file}")
    
    def run(self):
        """运行生成流程"""
        self.generate_report()
        print("✓ Report generation complete!")


if __name__ == "__main__":
    generator = HousePriceGenerator()
    generator.run()
