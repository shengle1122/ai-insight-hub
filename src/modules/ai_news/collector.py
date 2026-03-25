#!/usr/bin/env python3
"""
AI新闻数据采集模块
从多个源采集AI行业最新动态
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import re

DATA_DIR = Path("data/ai_news")
DATA_DIR.mkdir(parents=True, exist_ok=True)


class AINewsCollector:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data = {
            "date": self.today,
            "sources": {},
            "articles": []
        }
    
    def collect_hackernews(self, limit=20):
        """从 Hacker News 采集AI相关新闻"""
        try:
            # HN API: 获取最新文章
            url = "https://hacker-news.firebaseio.com/v0/newstories.json"
            response = requests.get(url, timeout=30)
            story_ids = response.json()[:limit]
            
            articles = []
            ai_keywords = [
                'ai', 'artificial intelligence', 'machine learning', 'deep learning',
                'llm', 'gpt', 'chatgpt', 'claude', 'gemini', 'neural', 'openai',
                'anthropic', 'model', 'training', 'inference', 'transformer'
            ]
            
            for story_id in story_ids:
                try:
                    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    story = requests.get(story_url, timeout=10).json()
                    
                    if not story or story.get('deleted') or story.get('dead'):
                        continue
                    
                    title = story.get('title', '').lower()
                    is_ai_related = any(kw in title for kw in ai_keywords)
                    
                    if is_ai_related:
                        articles.append({
                            "id": story_id,
                            "title": story.get('title'),
                            "url": story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            "score": story.get('score', 0),
                            "comments": story.get('descendants', 0),
                            "time": datetime.fromtimestamp(story.get('time', 0)).isoformat(),
                            "source": "hackernews"
                        })
                except Exception as e:
                    print(f"Error fetching story {story_id}: {e}")
                    continue
            
            self.data["sources"]["hackernews"] = articles
            print(f"✓ Collected {len(articles)} AI articles from Hacker News")
            return articles
            
        except Exception as e:
            print(f"Error collecting from Hacker News: {e}")
            return []
    
    def collect_arxiv(self, limit=10):
        """从 arXiv 采集最新AI论文"""
        try:
            # arXiv API
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            url = f"http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&start=0&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
            
            response = requests.get(url, timeout=30)
            content = response.text
            
            # 解析XML（简化版）
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            
            # arXiv namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            articles = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else ""
                summary = entry.find('atom:summary', ns).text if entry.find('atom:summary', ns) is not None else ""
                link = entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else ""
                published = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else ""
                
                # 清理标题和摘要
                title = ' '.join(title.split())
                summary = ' '.join(summary.split()[:100])  # 限制摘要长度
                
                articles.append({
                    "id": link.split('/')[-1] if '/' in link else link,
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "published": published,
                    "source": "arxiv"
                })
            
            self.data["sources"]["arxiv"] = articles
            print(f"✓ Collected {len(articles)} AI papers from arXiv")
            return articles
            
        except Exception as e:
            print(f"Error collecting from arXiv: {e}")
            return []
    
    def collect_github_trending(self):
        """采集GitHub Trending上的AI项目"""
        try:
            # GitHub trending 没有官方API，使用GitHub Search API
            url = "https://api.github.com/search/repositories"
            params = {
                "q": "topic:machine-learning OR topic:deep-learning OR topic:ai OR topic:llm created:>" + (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "sort": "stars",
                "order": "desc",
                "per_page": 15
            }
            
            headers = {}
            if os.getenv("GITHUB_TOKEN"):
                headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            data = response.json()
            
            articles = []
            for repo in data.get("items", []):
                articles.append({
                    "id": repo["id"],
                    "title": f"{repo['full_name']}: {repo['description'] or 'No description'}",
                    "url": repo["html_url"],
                    "stars": repo["stargazers_count"],
                    "language": repo["language"],
                    "source": "github"
                })
            
            self.data["sources"]["github"] = articles
            print(f"✓ Collected {len(articles)} trending AI repos from GitHub")
            return articles
            
        except Exception as e:
            print(f"Error collecting from GitHub: {e}")
            return []
    
    def save(self):
        """保存采集的数据"""
        output_file = DATA_DIR / f"{self.today}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✓ Data saved to {output_file}")
    
    def run(self):
        """运行采集流程"""
        print(f"🤖 Starting AI news collection for {self.today}...")
        self.collect_hackernews()
        self.collect_arxiv()
        self.collect_github_trending()
        self.save()
        print("✓ Collection complete!")


if __name__ == "__main__":
    collector = AINewsCollector()
    collector.run()
