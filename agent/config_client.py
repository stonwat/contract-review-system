"""Agent 通用配置加载与 HTTP 客户端。"""

import os
from pathlib import Path

import httpx
import yaml


class AgentConfig:
    """从 config.yaml 加载配置。"""

    def __init__(self, config_path: str | None = None) -> None:
        path = Path(config_path or os.environ.get("AGENT_CONFIG", "agent/config.yaml"))
        with path.open(encoding="utf-8") as f:
            self._cfg = yaml.safe_load(f)

        self.server_base_url: str = self._cfg["server"]["base_url"]
        self.server_api_key: str = self._cfg["server"]["api_key"]
        self.llm_base_url: str = self._cfg["llm"]["base_url"]
        self.llm_api_key: str = self._cfg["llm"]["api_key"]
        self.llm_model: str = self._cfg["llm"]["model"]
        self.front_signals: list[str] = self._cfg.get("signals", {}).get("front", [])
        self.back_signals: list[str] = self._cfg.get("signals", {}).get("back", [])

    def auth_headers(self) -> dict:
        return {"X-API-Key": self.server_api_key}


def make_client(config: AgentConfig) -> httpx.Client:
    """构造带认证头的同步 HTTP 客户端。"""
    return httpx.Client(
        base_url=config.server_base_url,
        headers=config.auth_headers(),
        timeout=60.0,
    )
