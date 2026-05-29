# ai_agent/smart_reply.py - 智能回复建议引擎
"""
根据聊天上下文智能推荐快捷回复
支持基于规则的快速建议和基于 LLM 的深度建议两种模式
"""

import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


# 快速回复模板 — 基于关键词匹配，无需 LLM 调用
QUICK_REPLIES: Dict[str, List[str]] = {
    "问候": {
        "patterns": ["你好", "hi", "hello", "嗨", "早上好", "下午好", "晚上好", "在吗"],
        "replies": ["你好呀！", "在的，有什么事吗？", "嗨~", "你好，有什么可以帮你的？"],
    },
    "告别": {
        "patterns": ["再见", "拜拜", "bye", "下次见", "先走了", "晚安"],
        "replies": ["再见！", "拜拜~", "下次再聊！", "晚安，好梦 🌙"],
    },
    "感谢": {
        "patterns": ["谢谢", "感谢", "多谢", "thanks", "thx"],
        "replies": ["不客气！", "举手之劳~", "能帮到你就好！", "别客气 😊"],
    },
    "同意": {
        "patterns": ["好的", "行", "可以", "没问题", "ok", "收到"],
        "replies": ["好的！", "收到！", "没问题~", "了解！"],
    },
    "疑问": {
        "patterns": ["怎么", "为什么", "什么", "哪里", "什么时候", "如何"],
        "replies": ["让我想想...", "这个问题我也在考虑", "我来查一下", "稍等，我看看"],
    },
}


class SmartReplyEngine:
    """智能回复建议引擎"""

    def __init__(self, ai_agent=None):
        self._ai_agent = ai_agent

    def get_quick_replies(self, message: str, count: int = 3) -> List[str]:
        """
        基于规则的快速回复建议（不调用 LLM，毫秒级返回）
        """
        text = message.strip().lower()
        matched = []

        for category, data in QUICK_REPLIES.items():
            for pattern in data["patterns"]:
                if pattern in text:
                    matched.extend(data["replies"])
                    break

        # 如果没有匹配到关键词，返回通用回复
        if not matched:
            matched = ["收到！", "好的", "了解", "嗯嗯", "继续说"]

        # 去重并限制数量
        seen = set()
        unique = []
        for r in matched:
            if r not in seen:
                seen.add(r)
                unique.append(r)
            if len(unique) >= count:
                break

        return unique

    def get_smart_replies(self, username: str, chat_history: str, count: int = 3) -> List[str]:
        """
        基于 LLM 的深度回复建议（需要调用 AI Agent）
        """
        if not self._ai_agent or not self._ai_agent.enabled:
            return self.get_quick_replies(chat_history.split("\n")[-1] if chat_history else "", count)

        try:
            result = self._ai_agent.suggest_reply(username, chat_history)
            # 解析 AI 返回的建议列表
            replies = self._parse_suggestions(result, count)
            return replies if replies else self.get_quick_replies("", count)
        except Exception as e:
            logger.error(f"智能回复建议失败: {e}")
            return self.get_quick_replies("", count)

    def _parse_suggestions(self, text: str, count: int) -> List[str]:
        """解析 AI 返回的建议文本"""
        replies = []
        # 尝试按行解析
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # 去除序号前缀
            cleaned = re.sub(r"^[\d]+[\.\)、]\s*", "", line)
            # 去除引号
            cleaned = cleaned.strip("""'""""""''"「」""")
            if cleaned and len(cleaned) <= 100:
                replies.append(cleaned)
            if len(replies) >= count:
                break
        return replies
