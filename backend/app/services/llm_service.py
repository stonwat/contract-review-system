"""LLM 调用封装。统一接口，通过环境变量配置模型。"""

import json
import re

import httpx

from app.config import settings
from app.core.exceptions import BusinessError


class LLMService:
    """LLM 调用客户端。"""

    def __init__(self) -> None:
        self.base_url = settings.llm_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    async def chat(self, prompt: str, system: str | None = None) -> str:
        """调用 LLM 完成对话。返回纯文本响应。"""
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"model": self.model, "messages": messages},
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise BusinessError(code=5001, message=f"LLM 调用失败: {e}") from e

    @staticmethod
    def _parse_json_response(text: str) -> dict:
        """从 LLM 响应中解析 JSON，兼容 markdown 代码块包裹。"""
        # 尝试提取 ```json ... ``` 块
        m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        json_str = m.group(1) if m else text

        # 去除首尾非 JSON 字符
        json_str = json_str.strip()
        start = json_str.find("{")
        end = json_str.rfind("}")
        if start >= 0 and end > start:
            json_str = json_str[start : end + 1]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 解析失败，返回原始文本
            return {"raw_text": text}


llm_service = LLMService()
