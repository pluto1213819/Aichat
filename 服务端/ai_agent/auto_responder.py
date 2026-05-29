# ai_agent/auto_responder.py - 自动应答引擎
"""
用户离线/暂离时，AI 代为自动回复
支持：全局开关、单用户开关、白名单/黑名单、回复频率控制
"""

import logging
import time
import threading
from typing import Dict, Set, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class AutoResponder:
    """
    自动应答管理器
    功能：
    - 每个用户可独立开启/关闭自动应答
    - 对同一发送者设定回复冷却（避免刷屏）
    - 白名单/黑名单控制
    """

    def __init__(self, ai_agent, cooldown_seconds: int = 60):
        self._ai_agent = ai_agent
        self._cooldown = cooldown_seconds
        self._lock = threading.Lock()

        # {username: enabled}
        self._user_enabled: Dict[str, bool] = {}
        # {(username, from_user): last_reply_timestamp}
        self._last_reply: Dict[tuple, float] = {}
        # {username: set(blacklisted_from_users)}
        self._blacklist: Dict[str, Set[str]] = defaultdict(set)
        # {username: set(whitelisted_from_users)}  — 空集表示允许所有人
        self._whitelist: Dict[str, Set[str]] = defaultdict(set)

    # ------------------------------------------------------------------ 开关
    def enable_for_user(self, username: str):
        with self._lock:
            self._user_enabled[username] = True
        logger.info(f"[自动应答] 已为用户 {username} 开启")

    def disable_for_user(self, username: str):
        with self._lock:
            self._user_enabled[username] = False
        logger.info(f"[自动应答] 已为用户 {username} 关闭")

    def is_enabled_for(self, username: str) -> bool:
        with self._lock:
            return self._user_enabled.get(username, False)

    # ------------------------------------------------------------------ 黑白名单
    def add_to_blacklist(self, username: str, blocked_user: str):
        with self._lock:
            self._blacklist[username].add(blocked_user)

    def remove_from_blacklist(self, username: str, blocked_user: str):
        with self._lock:
            self._blacklist[username].discard(blocked_user)

    def add_to_whitelist(self, username: str, allowed_user: str):
        with self._lock:
            self._whitelist[username].add(allowed_user)

    def clear_whitelist(self, username: str):
        with self._lock:
            self._whitelist[username].clear()

    # ------------------------------------------------------------------ 核心逻辑
    def should_auto_reply(self, username: str, from_user: str) -> bool:
        """
        判断是否应该自动回复
        """
        with self._lock:
            # 未开启
            if not self._user_enabled.get(username, False):
                return False

            # 在黑名单中
            if from_user in self._blacklist[username]:
                return False

            # 有白名单且不在白名单中
            if self._whitelist[username] and from_user not in self._whitelist[username]:
                return False

            # 冷却检查
            key = (username, from_user)
            last = self._last_reply.get(key, 0)
            if time.time() - last < self._cooldown:
                return False

        return True

    def process_message(self, username: str, from_user: str, message: str) -> Optional[str]:
        """
        处理一条消息，如果需要自动应答则返回回复内容，否则返回 None
        """
        if not self.should_auto_reply(username, from_user):
            return None

        reply = self._ai_agent.auto_reply(username, from_user, message)
        if reply:
            with self._lock:
                self._last_reply[(username, from_user)] = time.time()
            logger.info(f"[自动应答] {username} -> {from_user}: {reply[:50]}...")
        return reply

    def get_status(self, username: str) -> Dict:
        """获取某用户的自动应答状态"""
        with self._lock:
            return {
                "enabled": self._user_enabled.get(username, False),
                "cooldown": self._cooldown,
                "blacklist_count": len(self._blacklist[username]),
                "whitelist_count": len(self._whitelist[username]),
            }

    def cleanup(self):
        """清理过期的冷却记录"""
        now = time.time()
        with self._lock:
            expired = [k for k, v in self._last_reply.items() if now - v > self._cooldown * 10]
            for k in expired:
                del self._last_reply[k]
