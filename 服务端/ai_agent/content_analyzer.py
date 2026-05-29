# ai_agent/content_analyzer.py - 内容解析引擎
"""
对消息内容进行智能分析：摘要、关键词提取、翻译、情感分析等
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """
    内容解析引擎
    - 规则层：关键词提取、文本统计（不依赖 LLM）
    - AI 层：摘要、翻译、情感分析（依赖 AI Agent）
    """

    def __init__(self, ai_agent=None):
        self._ai_agent = ai_agent
        # 中文停用词（精简版）
        self._stopwords = set("的了是在我有和人这中大为上个国说也子时道出会要对开那里作生能如已公三")

    # ------------------------------------------------------------------ 规则层
    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """基于词频提取关键词（简单中文分词）"""
        # 提取中文词组（2-4字）和英文单词
        cn_words = re.findall(r"[\u4e00-\u9fff]{2,4}", text)
        en_words = re.findall(r"[a-zA-Z]{3,}", text.lower())

        all_words = [w for w in cn_words + en_words if w not in self._stopwords]
        freq = Counter(all_words)
        return [w for w, _ in freq.most_common(top_k)]

    def text_stats(self, text: str) -> Dict:
        """文本基本统计"""
        cn_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        en_words = len(re.findall(r"[a-zA-Z]+", text))
        digits = len(re.findall(r"\d", text))
        total_chars = len(text)
        lines = text.count("\n") + 1

        return {
            "total_chars": total_chars,
            "cn_chars": cn_chars,
            "en_words": en_words,
            "digits": digits,
            "lines": lines,
        }

    def detect_language(self, text: str) -> str:
        """简单语言检测"""
        cn_ratio = len(re.findall(r"[\u4e00-\u9fff]", text)) / max(len(text), 1)
        en_ratio = len(re.findall(r"[a-zA-Z]", text)) / max(len(text), 1)

        if cn_ratio > 0.3:
            return "zh"
        elif en_ratio > 0.5:
            return "en"
        return "mixed"

    def extract_urls(self, text: str) -> List[str]:
        """提取 URL"""
        return re.findall(r"https?://[^\s<>\"']+", text)

    def extract_at_mentions(self, text: str) -> List[str]:
        """提取 @提及"""
        return re.findall(r"@(\w+)", text)

    # ------------------------------------------------------------------ AI 层
    def summarize(self, username: str, text: str) -> str:
        """AI 摘要"""
        if not self._ai_agent or not self._ai_agent.enabled:
            # 无 AI 时的简单摘要：取前100字
            return text[:100] + ("..." if len(text) > 100 else "")
        return self._ai_agent.summarize(username, text)

    def translate(self, username: str, text: str, target: str = "英文") -> str:
        """AI 翻译"""
        if not self._ai_agent or not self._ai_agent.enabled:
            return "AI 翻译服务未启用"
        return self._ai_agent.translate(username, text, target)

    def polish(self, username: str, text: str) -> str:
        """AI 润色"""
        if not self._ai_agent or not self._ai_agent.enabled:
            return text
        return self._ai_agent.polish(username, text)

    def sentiment(self, username: str, text: str) -> str:
        """AI 情感分析"""
        if not self._ai_agent or not self._ai_agent.enabled:
            return "AI 情感分析服务未启用"
        return self._ai_agent.analyze_sentiment(username, text)
