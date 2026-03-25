#!/usr/bin/env python3
"""
AI新闻简报生成器
使用LLM对采集的数据进行分析和总结
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import re

DATA_DIR = Path("data/ai_news")
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)


class AINewsGenerator:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data_file = DATA_DIR / f"{self.today}.json"
        self.report_file = DOCS_DIR / "ai-news-report.md"
    
    def load_data(self) -> Dict:
        """加载采集的数据"""
        if not self.data_file.exists():
            # 尝试加载最近的数据
            files = sorted(DATA_DIR.glob("*.json"), reverse=True)
            if files:
                self.data_file = files[0]
            else:
                raise FileNotFoundError("No data file found")
        
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def analyze_with_llm(self, data: Dict) -> str:
        """使用LLM分析并生成简报"""
        try:
            # 尝试使用 OpenAI API
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️ OPENAI_API_KEY not set, using fallback analysis")
                return self.fallback_analysis(data)
            
            client = openai.OpenAI(api_key=api_key)
            
            # 构建提示
            hn_articles = data.get("sources", {}).get("hackernews", [])
            arxiv_papers = data.get("sources", {}).get("arxiv", [])
            github_repos = data.get("sources", {}).get("github", [])
            
            prompt = f"""请作为一位专业的AI行业分析师，对以下今日AI行业动态进行分析和总结，生成一份中文简报。

## 数据来源
- Hacker News热门AI讨论: {len(hn_articles)}条
- arXiv最新论文: {len(arxiv_papers)}条  
- GitHub热门项目: {len(github_repos)}条

## Hacker News热门讨论
"""
            for i, item in enumerate(hn_articles[:10], 1):
                prompt += f"{i}. {item['title']} (热度: {item.get('score', 0)}分, {item.get('comments', 0)}评论)\n"
            
            prompt += "\n## arXiv最新论文\n"
            for i, item in enumerate(arxiv_papers[:5], 1):
                prompt += f"{i}. {item['title'][:100]}...\n"
            
            prompt += "\n## GitHub热门项目\n"
            for i, item in enumerate(github_repos[:5], 1):
                prompt += f"{i}. {item['title'][:80]}... (⭐{item.get('stars', 0)})\n"
            
            prompt += """

## 简报要求
请生成一份结构化的中文简报，包含：
1. **核心动态**（3-5条最重要的行业新闻/动态）
2. **技术趋势**（从技术角度分析当前热点）
3. **值得关注**（推荐2-3个值得深入了解的论文或项目）
4. **一句话总结**（用一句话概括今日AI行业的主要动向）

使用Markdown格式，语言简洁专业。"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一位专业的AI行业分析师，擅长从海量信息中提炼核心价值。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error using LLM: {e}")
            return self.fallback_analysis(data)
    
    def fallback_analysis(self, data: Dict) -> str:
        """当LLM不可用时，使用简单的规则生成简报"""
        hn_articles = data.get("sources", {}).get("hackernews", [])
        arxiv_papers = data.get("sources", {}).get("arxiv", [])
        github_repos = data.get("sources", {}).get("github", [])
        
        report = f"""## 🎯 核心动态

"""
        # 按热度排序HN文章
        sorted_hn = sorted(hn_articles, key=lambda x: x.get('score', 0), reverse=True)
        for item in sorted_hn[:5]:
            report += f"- **{item['title']}**\n"
            report += f"  - 来源: Hacker News | 热度: {item.get('score', 0)}分\n"
            report += f"  - 链接: {item['url']}\n\n"
        
        report += """## 📊 技术趋势

基于今日数据采集，AI领域关注热点：
"""
        # 简单关键词统计
        keywords = {}
        all_text = ' '.join([item['title'] for item in hn_articles + arxiv_papers])
        for kw in ['LLM', 'OpenAI', 'training', 'model', 'GPT', 'Claude', 'Gemini']:
            count = all_text.lower().count(kw.lower())
            if count > 0:
                keywords[kw] = count
        
        for kw, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"- **{kw}**: 出现 {count} 次\n"
        
        report += """

## 🔍 值得关注

### 最新论文
"""
        for item in arxiv_papers[:3]:
            report += f"- [{item['title'][:60]}...]({item['url']})\n"
        
        report += """
### 热门项目
"""
        for item in github_repos[:3]:
            report += f"- [{item['title'][:50]}...]({item['url']}) - ⭐ {item.get('stars', 0)}\n"
        
        report += """

## 💡 一句话总结

今日AI行业继续聚焦于大语言模型技术和开源项目的快速发展，社区讨论活跃。"""
        
        return report
    
    def generate_report(self):
        """生成完整的报告"""
        print(f"📄 Generating AI news report for {self.today}...")
        
        data = self.load_data()
        analysis = self.analyze_with_llm(data)
        
        report = f"""# 🤖 AI行业动态简报

**生成时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}

---

{analysis}

---

*数据来源: Hacker News, arXiv, GitHub | 自动更新于每日8:00*
"""
        
        # 保存报告
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✓ Report saved to {self.report_file}")
        return report
    
    def run(self):
        """运行生成流程"""
        self.generate_report()
        print("✓ Report generation complete!")


if __name__ == "__main__":
    generator = AINewsGenerator()
    generator.run()
