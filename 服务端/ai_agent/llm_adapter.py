# ai_agent/llm_adapter.py - LLM 服务适配器
"""
统一的 LLM 调用适配层，支持 OpenAI / DeepSeek / 本地大模型
采用适配器模式，切换模型只需更换 adapter 实例
"""

import json
import logging
import urllib.request
import urllib.error
import ssl
import time
from typing import Optional, List, Dict, Generator

logger = logging.getLogger(__name__)


class LLMAdapter:
    """LLM 适配器基类"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "",
                 timeout: int = 30, max_tokens: int = 2048, temperature: float = 0.7):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._ssl_ctx = ssl.create_default_context()
        self._ssl_ctx.check_hostname = False
        self._ssl_ctx.verify_mode = ssl.CERT_NONE

    def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求，返回纯文本回复"""
        raise NotImplementedError

    def chat_stream(self, messages: List[Dict], **kwargs) -> Generator[str, None, None]:
        """流式对话（默认退化为非流式）"""
        yield self.chat(messages, **kwargs)

    def _do_request(self, url: str, headers: dict, payload: dict, stream: bool = False):
        """底层 HTTP 请求"""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout, context=self._ssl_ctx)
            if stream:
                return resp
            return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            logger.error(f"LLM HTTP {e.code}: {err_body}")
            raise RuntimeError(f"LLM 请求失败 (HTTP {e.code}): {err_body[:200]}")
        except Exception as e:
            logger.error(f"LLM 请求异常: {e}")
            raise


class OpenAIAdapter(LLMAdapter):
    """OpenAI 兼容接口适配器（同时支持 DeepSeek、Moonshot、通义千问等兼容接口）"""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1",
                 model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(api_key, base_url, model, **kwargs)

    def chat(self, messages: List[Dict], **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": False,
        }
        data = self._do_request(url, headers, payload)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"解析 OpenAI 响应失败: {data}")
            return "抱歉，AI 服务返回了异常响应，请稍后重试。"

    def chat_stream(self, messages: List[Dict], **kwargs) -> Generator[str, None, None]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": True,
        }
        try:
            resp = self._do_request(url, headers, payload, stream=True)
            buffer = ""
            for chunk in iter(lambda: resp.read(1024), b""):
                buffer += chunk.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        return
                    try:
                        obj = json.loads(data_str)
                        delta = obj["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        except Exception as e:
            logger.error(f"流式请求失败，退化为非流式: {e}")
            yield self.chat(messages, **kwargs)


class DeepSeekAdapter(OpenAIAdapter):
    """DeepSeek 专用适配器（接口兼容 OpenAI）"""

    def __init__(self, api_key: str, model: str = "deepseek-chat", **kwargs):
        super().__init__(
            api_key=api_key,
            base_url=kwargs.pop("base_url", "https://api.deepseek.com/v1"),
            model=model,
            **kwargs,
        )


class MockAdapter(LLMAdapter):
    """
    本地模拟适配器 — 不依赖外部 API，用于演示 / 离线模式
    基于关键词匹配 + 模板生成简单回复
    """

    TEMPLATES = {
        "问候": ["你好呀！有什么我可以帮你的吗？😊", "嗨！很高兴为你服务！", "你好！我是 Nova AI 智能助手。"],
        "天气": ["抱歉，我目前无法查询实时天气，建议您查看天气预报应用。"],
        "帮助": ["我可以帮你：\n1. 智能问答\n2. 内容摘要\n3. 翻译辅助\n4. 自动应答\n有什么需要尽管问我！"],
        "谢谢": ["不客气！有需要随时找我 😊", "很高兴能帮到你！", "不用谢，这是我应该做的！"],
        "默认": [
            "这是个好问题！让我想想...",
            "我理解你的意思，我的建议是...",
            "收到！我来帮你分析一下这个问题。",
            "好的，我来处理这个请求。",
        ],
    }

    def chat(self, messages: List[Dict], **kwargs) -> str:
        import random
        user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_msg = m.get("content", "")
                break

        text = user_msg.lower()
        if any(w in text for w in ["你好", "hi", "hello", "嗨", "hey"]):
            pool = self.TEMPLATES["问候"]
        elif any(w in text for w in ["天气", "气温", "下雨"]):
            pool = self.TEMPLATES["天气"]
        elif any(w in text for w in ["帮助", "功能", "你能做什么", "怎么用"]):
            pool = self.TEMPLATES["帮助"]
        elif any(w in text for w in ["谢谢", "感谢", "多谢", "thanks"]):
            pool = self.TEMPLATES["谢谢"]
        else:
            pool = self.TEMPLATES["默认"]

        time.sleep(0.3)  # 模拟网络延迟
        return random.choice(pool)
