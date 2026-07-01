"""批量处理目录下所有合同文件。

用法：
    python -m agent.batch_process --dir ./projects/2025年项目/
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from agent.config_client import AgentConfig
from agent.ocr_extract import process_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".pdf", ".docx", ".doc", ".xls", ".xlsx", ".jpg", ".png"}


async def process_directory(dir_path: Path, config: AgentConfig) -> None:
    """递归处理目录下所有支持的文件。"""
    files = [p for p in dir_path.rglob("*") if p.suffix.lower() in SUPPORTED_EXTS]
    logger.info("发现 %d 个待处理文件", len(files))

    for f in files:
        try:
            result = await process_file(f, config)
            logger.info("已处理: %s -> %s", f.name, result.get("data"))
        except Exception as e:  # noqa: BLE001
            logger.error("处理失败: %s, 错误: %s", f.name, e)


def main() -> None:
    parser = argparse.ArgumentParser(description="批量处理合同文件")
    parser.add_argument("--dir", required=True, help="合同文件所在目录")
    parser.add_argument("--config", default="agent/config.yaml", help="配置文件路径")
    args = parser.parse_args()

    config = AgentConfig(args.config)
    asyncio.run(process_directory(Path(args.dir), config))


if __name__ == "__main__":
    main()
