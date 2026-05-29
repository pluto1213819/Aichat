# ai_agent/agent_core.py - AI Agent 核心引擎
"""
AI Agent 核心：管理对话上下文、路由请求到各子模块、维护会话状态
"""

import logging
import time
import json
import threading
from typing import Optional, Dict, List
from collections import defaultdict

from ai_agent.llm_adapter import LLMAdapter, OpenAIAdapter, DeepSeekAdapter, MockAdapter

logger = logging.getLogger(__name__)

# ---------- 系统提示词 ----------
SYSTEM_PROMPT = """你是 Nova AI 智能助手，嵌入在 Nova Chatting 即时通讯系统中。
你的职责：
1. 回答用户的各种问题，提供准确、有帮助的信息。
2. 当用户要求时，对消息或文本进行摘要、翻译、润色。
3. 帮助用户起草回复、总结聊天记录。
4. 保持友善、专业、简洁的沟通风格。
5. 如果收到 [系统消息] 标记的内容，说明是自动应答场景，请以用户的口吻礼貌回复。
请用中文回答，除非用户用其他语言提问。
"""

AUTO_REPLY_PROMPT = """你正在代替一个暂时离开的用户自动回复消息。
请以该用户的口吻礼貌回复，告知对方用户暂时不在，稍后会回复。
用户名：{username}
对方发送的消息：{message}
"""


class ConversationContext:
    """单个对话的上下文管理"""

    def __init__(self, max_history: int = 20):
        self.messages: List[Dict] = []
        self.max_history = max_history
        self.last_active = time.time()
        self.created_at = time.time()

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self.last_active = time.time()
        # 超过上限则裁剪旧消息（保留 system）
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def get_messages(self, system_prompt: str = "") -> List[Dict]:
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(self.messages)
        return msgs

    def clear(self):
        self.messages.clear()
        self.last_active = time.time()


class AIAgent:
    """
    AI Agent 智能体核心类
    - 管理每个用户的对话上下文
    - 调用 LLM 获取回复
    - 提供摘要、翻译、智能建议等扩展能力
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._lock = threading.Lock()
        self._contexts: Dict[str, ConversationContext] = defaultdict(
            lambda: ConversationContext(max_history=self.config.get("max_history", 20))
        )
        self._adapter: Optional[LLMAdapter] = None
        self._enabled = True
        self._init_adapter()

    # ------------------------------------------------------------------ 初始化
    def _init_adapter(self):
        """根据配置初始化 LLM 适配器"""
        provider = self.config.get("provider", "mock")
        api_key = self.config.get("api_key", "")
        base_url = self.config.get("base_url", "")
        model = self.config.get("model", "")
        timeout = self.config.get("timeout", 30)
        max_tokens = self.config.get("max_tokens", 2048)
        temperature = self.config.get("temperature", 0.7)

        if provider == "openai" and api_key:
            self._adapter = OpenAIAdapter(
                api_key=api_key, base_url=base_url or "https://api.openai.com/v1",
                model=model or "gpt-3.5-turbo",
                timeout=timeout, max_tokens=max_tokens, temperature=temperature,
            )
            logger.info(f"[AI Agent] 使用 OpenAI 适配器, model={model}")
        elif provider == "deepseek" and api_key:
            self._adapter = DeepSeekAdapter(
                api_key=api_key, model=model or "deepseek-chat",
                timeout=timeout, max_tokens=max_tokens, temperature=temperature,
            )
            logger.info(f"[AI Agent] 使用 DeepSeek 适配器, model={model}")
        elif api_key and base_url:
            # 通用 OpenAI 兼容接口
            self._adapter = OpenAIAdapter(
                api_key=api_key, base_url=base_url, model=model or "gpt-3.5-turbo",
                timeout=timeout, max_tokens=max_tokens, temperature=temperature,
            )
            logger.info(f"[AI Agent] 使用通用 OpenAI 兼容适配器, base_url={base_url}")
        else:
            self._adapter = MockAdapter()
            logger.info("[AI Agent] 未配置 API Key，使用本地模拟适配器（MockAdapter）")

    # ------------------------------------------------------------------ 公共接口
    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        logger.info(f"[AI Agent] {'已启用' if value else '已禁用'}")

    def reload_config(self, config: dict):
        """热更新配置"""
        self.config = config
        with self._lock:
            self._init_adapter()
        logger.info("[AI Agent] 配置已热更新")

    def get_context(self, username: str) -> ConversationContext:
        with self._lock:
            return self._contexts[username]

    def clear_context(self, username: str):
        with self._lock:
            if username in self._contexts:
                self._contexts[username].clear()

    def cleanup_stale_contexts(self, max_idle: int = 3600):
        """清理长时间不活跃的对话上下文"""
        now = time.time()
        with self._lock:
            stale = [u for u, ctx in self._contexts.items()
                     if now - ctx.last_active > max_idle]
            for u in stale:
                del self._contexts[u]
            if stale:
                logger.info(f"[AI Agent] 清理了 {len(stale)} 个不活跃对话上下文")

    # ------------------------------------------------------------------ 对话
    def chat(self, username: str, user_message: str, system_prompt: str = "") -> str:
        """
        普通对话入口
        :param username: 发送者用户名
        :param user_message: 用户消息内容
        :param system_prompt: 可选的自定义系统提示词
        :return: AI 回复文本
        """
        if not self._enabled:
            return "AI 智能助手当前已禁用，请联系管理员开启。"

        ctx = self.get_context(username)
        ctx.add_message("user", user_message)

        prompt = system_prompt or SYSTEM_PROMPT
        messages = ctx.get_messages(system_prompt=prompt)

        try:
            reply = self._adapter.chat(messages)
            ctx.add_message("assistant", reply)
            return reply
        except Exception as e:
            logger.error(f"[AI Agent] 对话失败 ({username}): {e}")
            return f"AI 服务暂时不可用，请稍后重试。（错误：{str(e)[:100]}）"

    # ------------------------------------------------------------------ 自动应答
    def auto_reply(self, username: str, from_user: str, message: str) -> str:
        """
        自动应答：用户离线/暂离时代为回复
        :param username: 被代替回复的用户
        :param from_user: 发消息的人
        :param message: 消息内容
        :return: 自动回复文本
        """
        if not self._enabled:
            return ""

        prompt = AUTO_REPLY_PROMPT.format(username=username, message=message)
        try:
            reply = self._adapter.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
            return reply
        except Exception as e:
            logger.error(f"[AI Agent] 自动应答失败: {e}")
            return ""

    # ------------------------------------------------------------------ 内容分析
    def summarize(self, username: str, text: str) -> str:
        """文本摘要"""
        prompt = f"请对以下内容进行简洁的摘要，突出关键信息（不超过100字）：\n\n{text}"
        return self.chat(username, prompt, system_prompt=SYSTEM_PROMPT)

    def translate(self, username: str, text: str, target_lang: str = "英文") -> str:
        """翻译"""
        prompt = f"请将以下内容翻译成{target_lang}，保持原意，语言自然流畅：\n\n{text}"
        return self.chat(username, prompt, system_prompt=SYSTEM_PROMPT)

    def polish(self, username: str, text: str) -> str:
        """润色文本"""
        prompt = f"请帮我润色以下文字，使其更通顺、专业，保持原意：\n\n{text}"
        return self.chat(username, prompt, system_prompt=SYSTEM_PROMPT)

    def analyze_sentiment(self, username: str, text: str) -> str:
        """情感分析"""
        prompt = f"请分析以下文本的情感倾向（积极/消极/中性），并简要说明原因：\n\n{text}"
        return self.chat(username, prompt, system_prompt=SYSTEM_PROMPT)

    # ------------------------------------------------------------------ 智能建议
    def suggest_reply(self, username: str, chat_history: str) -> str:
        """根据聊天记录建议回复"""
        prompt = (
            f"以下是最近的聊天记录，请根据上下文建议3条合适的回复（简短、自然、符合对话场景）：\n\n"
            f"{chat_history}"
        )
        return self.chat(username, prompt, system_prompt=SYSTEM_PROMPT)

    # ------------------------------------------------------------------ 群聊助手
    def group_assistant(self, group_name: str, message: str) -> str:
        """群聊 AI 助手"""
        prompt = (
            f"你是一个群聊助手，群名称为「{group_name}」。"
            f"请根据群聊消息提供有帮助的回复。\n\n"
            f"消息内容：{message}"
        )
        try:
            return self._adapter.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
        except Exception as e:
            logger.error(f"[AI Agent] 群聊助手失败: {e}")
            return ""
