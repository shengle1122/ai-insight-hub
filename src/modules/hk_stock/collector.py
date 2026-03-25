#!/usr/bin/env python3
"""
港股行情数据采集模块
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/hk_stock")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 主要港股指数和ETF
HK_INDICES = {
    "HSI": {"name": "恒生指数", "symbol": "^HSI"},
    "HSCEI": {"name": "恒生国企指数", "symbol": "^HSCE"},
    "HSTECH": {"name": "恒生科技指数", "symbol": "^HSTECH"},
}

# 热门港股
HOT_STOCKS = {
    "0700.HK": "腾讯控股",
    "9988.HK": "阿里巴巴-SW",
    "3690.HK": "美团-W",
    "1810.HK": "小米集团-W",
    "2318.HK": "中国平安",
    "1299.HK": "友邦保险",
    "0005.HK": "汇丰控股",
    "0883.HK": "中国海洋石油",
}


class HKStockCollector:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data = {
            "date": self.today,
            "indices": {},
            "stocks": {},
            "market_summary": {}
        }
    
    def fetch_yahoo_data(self, symbol: str, period: str = "7d"):
        """从Yahoo Finance获取数据"""
        try:
            # Yahoo Finance API endpoint
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            # 计算日期范围
            end = int(datetime.now().timestamp())
            if period == "7d":
                start = int((datetime.now() - timedelta(days=7)).timestamp())
            elif period == "30d":
                start = int((datetime.now() - timedelta(days=30)).timestamp())
            else:
                start = int((datetime.now() - timedelta(days=7)).timestamp())
            
            params = {
                "period1": start,
                "period2": end,
                "interval": "1d"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            data = response.json()
            
            if data.get("chart", {}).get("error"):
                print(f"Error fetching {symbol}: {data['chart']['error']}")
                return None
            
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            prices = result["indicators"]["quote"][0]
            
            df_data = {
                "date": [datetime.fromtimestamp(t).strftime("%Y-%m-%d") for t in timestamps],
                "open": prices["open"],
                "high": prices["high"],
                "low": prices["low"],
                "close": prices["close"],
                "volume": prices["volume"]
            }
            
            return df_data
            
        except Exception as e:
            print(f"Error fetching Yahoo data for {symbol}: {e}")
            return None
    
    def collect_indices(self):
        """采集指数数据"""
        print("📊 Collecting HK indices data...")
        
        for code, info in HK_INDICES.items():
            try:
                data = self.fetch_yahoo_data(info["symbol"])
                if data:
                    # 计算涨跌
                    closes = [c for c in data["close"] if c is not None]
                    if len(closes) >= 2:
                        latest = closes[-1]
                        prev = closes[-2]
                        change = latest - prev
                        change_pct = (change / prev) * 100
                        
                        self.data["indices"][code] = {
                            "name": info["name"],
                            "symbol": info["symbol"],
                            "latest": round(latest, 2),
                            "change": round(change, 2),
                            "change_pct": round(change_pct, 2),
                            "history": [
                                {"date": d, "close": round(c, 2) if c else None}
                                for d, c in zip(data["date"], data["close"])
                            ]
                        }
                        print(f"  ✓ {info['name']}: {latest:.2f} ({change_pct:+.2f}%)")
            except Exception as e:
                print(f"  ✗ Error collecting {code}: {e}")
    
    def collect_stocks(self):
        """采集个股数据"""
        print("📈 Collecting HK stocks data...")
        
        for symbol, name in HOT_STOCKS.items():
            try:
                data = self.fetch_yahoo_data(symbol)
                if data:
                    closes = [c for c in data["close"] if c is not None]
                    if len(closes) >= 2:
                        latest = closes[-1]
                        prev = closes[-2]
                        change = latest - prev
                        change_pct = (change / prev) * 100
                        
                        # 计算7日统计
                        week_high = max([h for h in data["high"] if h is not None])
                        week_low = min([l for l in data["low"] if l is not None])
                        
                        self.data["stocks"][symbol] = {
                            "name": name,
                            "latest": round(latest, 2),
                            "change": round(change, 2),
                            "change_pct": round(change_pct, 2),
                            "week_high": round(week_high, 2),
                            "week_low": round(week_low, 2),
                            "volume": int(data["volume"][-1]) if data["volume"][-1] else 0
                        }
                        print(f"  ✓ {name}: {latest:.2f} ({change_pct:+.2f}%)")
            except Exception as e:
                print(f"  ✗ Error collecting {symbol}: {e}")
    
    def calculate_market_summary(self):
        """计算市场概览"""
        stocks = self.data["stocks"]
        
        if not stocks:
            return
        
        up_count = sum(1 for s in stocks.values() if s["change"] > 0)
        down_count = sum(1 for s in stocks.values() if s["change"] < 0)
        flat_count = len(stocks) - up_count - down_count
        
        # 涨跌幅最大的
        sorted_by_change = sorted(stocks.items(), key=lambda x: x[1]["change_pct"], reverse=True)
        top_gainer = sorted_by_change[0] if sorted_by_change else None
        top_loser = sorted_by_change[-1] if sorted_by_change else None
        
        self.data["market_summary"] = {
            "up_count": up_count,
            "down_count": down_count,
            "flat_count": flat_count,
            "top_gainer": {
                "symbol": top_gainer[0],
                "name": top_gainer[1]["name"],
                "change_pct": top_gainer[1]["change_pct"]
            } if top_gainer else None,
            "top_loser": {
                "symbol": top_loser[0],
                "name": top_loser[1]["name"],
                "change_pct": top_loser[1]["change_pct"]
            } if top_loser else None
        }
    
    def save(self):
        """保存数据"""
        output_file = DATA_DIR / f"{self.today}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✓ Data saved to {output_file}")
    
    def run(self):
        """运行采集流程"""
        print(f"📈 Starting HK stock data collection for {self.today}...")
        self.collect_indices()
        self.collect_stocks()
        self.calculate_market_summary()
        self.save()
        print("✓ Collection complete!")


if __name__ == "__main__":
    collector = HKStockCollector()
    collector.run()
