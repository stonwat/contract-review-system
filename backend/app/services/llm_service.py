"""LLM 调用封装。统一接口，通过环境变量配置模型。"""

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

    async def compare_terms(
        self, term_type: str, front_terms: str, back_terms: str
    ) -> dict:
        """比对两份合同的某类条款。返回 {"match": "一致/不一致", "diff_detail": "..."}。"""
        prompt = (
            f"你是合同审查专家。请比对以下两份合同的{term_type}条款，判断是否实质一致。\n"
            f"若不一致，具体描述差异。\n\n"
            f"前项合同{term_type}条款：\n{front_terms}\n\n"
            f"后项合同{term_type}条款：\n{back_terms}\n\n"
            f'输出JSON：{{ "match": "一致/不一致", "diff_detail": "具体差异描述" }}'
        )
        text = await self.chat(prompt)
        # 实际项目应做 JSON 解析与容错，此处骨架返回原文
        return {"raw": text}


llm_service = LLMService()
