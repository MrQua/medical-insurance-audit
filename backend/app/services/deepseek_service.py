"""DeepSeek 服务 - 封装 DeepSeek API 调用"""
import json
import httpx
from typing import AsyncGenerator, Optional, Dict, Any, List

from app.config import settings


class DeepSeekService:
    """DeepSeek 服务封装"""

    def __init__(self):
        self.api_base = settings.deepseek_base_url
        self.api_key = settings.deepseek_api_key
        self.model = settings.deepseek_model
        self.chat_api_url = f"{self.api_base}/chat/completions"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """非流式对话"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.chat_api_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """流式对话"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                self.chat_api_url,
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue


# 全局服务实例
deepseek_service = DeepSeekService()
