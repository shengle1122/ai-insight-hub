#!/usr/bin/env python3
"""
房价趋势数据采集模块
由于真实房价数据API较难获取，这里提供模拟数据和数据源说明
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import random

DATA_DIR = Path("data/house_price")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 重点城市列表
CITIES = {
    "hangzhou": {"name": "杭州", "tier": "新一线"},
    "shanghai": {"name": "上海", "tier": "一线"},
    "beijing": {"name": "北京", "tier": "一线"},
    "shenzhen": {"name": "深圳", "tier": "一线"},
    "guangzhou": {"name": "广州", "tier": "一线"},
    "chengdu": {"name": "成都", "tier": "新一线"},
    "wuhan": {"name": "武汉", "tier": "新一线"},
    "nanjing": {"name": "南京", "tier": "新一线"},
}

# 杭州各区
HANGZHOU_DISTRICTS = {
    "gongshu": "拱墅区",
    "shangcheng": "上城区",
    "xihu": "西湖区",
    "binjiang": "滨江区",
    "xiacheng": "下城区",
    "jianggan": "江干区",
    "xiaoshan": "萧山区",
    "yuhang": "余杭区",
}


class HousePriceCollector:
    """
    房价数据采集器
    
    注意：由于房价数据多为商业数据，这里提供：
    1. 模拟数据（用于演示）
    2. 真实数据源接入指南
    """
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data = {
            "date": self.today,
            "cities": {},
            "hangzhou_detail": {},
            "data_source": "模拟数据（演示用）",
            "disclaimer": "本数据仅供演示，实际使用时请接入真实数据源"
        }
    
    def generate_mock_data(self):
        """生成模拟数据（演示用）"""
        print("🏠 Generating mock house price data...")
        print("  Note: Replace with real data source for production")
        
        base_prices = {
            "shanghai": 68000,
            "beijing": 65000,
            "shenzhen": 58000,
            "guangzhou": 38000,
            "hangzhou": 32000,
            "nanjing": 28000,
            "chengdu": 18000,
            "wuhan": 17000,
        }
        
        # 生成城市数据
        for city_code, city_info in CITIES.items():
            base = base_prices.get(city_code, 20000)
            
            # 生成30天趋势
            trend = []
            current = base
            for i in range(30, 0, -1):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                # 随机波动 -0.5% ~ +0.5%
                change = random.uniform(-0.005, 0.005)
                current = current * (1 + change)
                trend.append({
                    "date": date,
                    "price": round(current, 0),
                    "change_pct": round(change * 100, 2)
                })
            
            # 计算月度变化
            month_change = (trend[-1]["price"] - trend[0]["price"]) / trend[0]["price"] * 100
            
            self.data["cities"][city_code] = {
                "name": city_info["name"],
                "tier": city_info["tier"],
                "avg_price": round(trend[-1]["price"], 0),
                "unit": "元/平方米",
                "month_change_pct": round(month_change, 2),
                "trend": trend[-7:]  # 最近7天
            }
            
            print(f"  ✓ {city_info['name']}: {self.data['cities'][city_code]['avg_price']:.0f} 元/㎡")
    
    def generate_hangzhou_detail(self):
        """生成杭州各区详细数据"""
        print("🏠 Generating Hangzhou district data...")
        
        district_multipliers = {
            "gongshu": 1.15,
            "shangcheng": 1.20,
            "xihu": 1.25,
            "binjiang": 1.30,
            "xiacheng": 1.10,
            "jianggan": 1.05,
            "xiaoshan": 0.75,
            "yuhang": 0.85,
        }
        
        hangzhou_base = self.data["cities"].get("hangzhou", {}).get("avg_price", 32000)
        
        for district_code, district_name in HANGZHOU_DISTRICTS.items():
            multiplier = district_multipliers.get(district_code, 1.0)
            base_price = hangzhou_base * multiplier
            
            # 生成趋势
            trend = []
            current = base_price
            for i in range(30, 0, -1):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                change = random.uniform(-0.008, 0.008)
                current = current * (1 + change)
                trend.append({
                    "date": date,
                    "price": round(current, 0),
                    "change_pct": round(change * 100, 2)
                })
            
            month_change = (trend[-1]["price"] - trend[0]["price"]) / trend[0]["price"] * 100
            
            self.data["hangzhou_detail"][district_code] = {
                "name": district_name,
                "avg_price": round(trend[-1]["price"], 0),
                "unit": "元/平方米",
                "month_change_pct": round(month_change, 2),
                "trend": trend[-7:]
            }
            
            print(f"  ✓ {district_name}: {self.data['hangzhou_detail'][district_code]['avg_price']:.0f} 元/㎡")
    
    def add_real_data_sources_guide(self):
        """添加真实数据源接入指南"""
        self.data["real_data_sources"] = {
            "链家": {
                "url": "https://www.lianjia.com/",
                "method": "爬虫/API申请",
                "coverage": "全国主要城市",
                "update_frequency": "日更"
            },
            "贝壳找房": {
                "url": "https://www.ke.com/",
                "method": "API（需申请）",
                "coverage": "全国300+城市",
                "update_frequency": "日更"
            },
            "安居客": {
                "url": "https://www.anjuke.com/",
                "method": "爬虫/数据合作",
                "coverage": "全国城市",
                "update_frequency": "周更"
            },
            "国家统计局": {
                "url": "https://data.stats.gov.cn/",
                "method": "官方API",
                "coverage": "70个大中城市",
                "update_frequency": "月度"
            }
        }
    
    def save(self):
        """保存数据"""
        output_file = DATA_DIR / f"{self.today}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✓ Data saved to {output_file}")
    
    def run(self):
        """运行采集流程"""
        print(f"🏠 Starting house price data collection for {self.today}...")
        print("⚠️  当前使用模拟数据，请根据real_data_sources配置真实数据源")
        
        self.generate_mock_data()
        self.generate_hangzhou_detail()
        self.add_real_data_sources_guide()
        self.save()
        
        print("✓ Collection complete!")
        print("\n💡 提示: 如需接入真实数据，请参考 data/house_price/<date>.json 中的 real_data_sources 字段")


if __name__ == "__main__":
    collector = HousePriceCollector()
    collector.run()
