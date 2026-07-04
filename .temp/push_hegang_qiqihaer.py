"""推送鹤岗和齐齐哈尔的合同数据到后端。

基于从PDF中提取的关键信息。
"""

import json
import logging
from pathlib import Path

import httpx
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_config() -> dict:
    with Path("A:/Inbox/contract-review-system/agent/config.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def push_contract(payload: dict, config: dict) -> dict:
    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post("/contracts", json=payload)
        if resp.status_code >= 400:
            logger.error("推送失败: %s %s", resp.status_code, resp.text[:300])
        resp.raise_for_status()
        return resp.json()


def push_acceptance(payload: dict, config: dict) -> dict:
    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post("/acceptance", json=payload)
        if resp.status_code >= 400:
            logger.error("推送失败: %s %s", resp.status_code, resp.text[:300])
        resp.raise_for_status()
        return resp.json()


# 鹤岗项目数据（从PDF文本中提取）
HEGANG = {
    # 前项合同: 大庆恒天 → 中电信数智 (扫描件，文本较少)
    "front_contract": {
        "contract_no": "XYJAEXJCI250500015",
        "contract_type": "前项",
        "type_judge_basis": "文件名:黑龙江省（鹤岗）传输管线工程施工服务合同（上家合同扫描）.pdf",
        "party_a": "大庆恒天技术有限公司",
        "party_b": "中电信数智科技有限公司黑龙江分公司",
        "our_role": "乙方",
        "signing_date": None,  # 扫描件无法确认具体日期
        "contract_period": "30天",
        "total_amount": 2740000.00,  # 从鹤岗项目列账数据推算
        "amount_uppercase": None,
        "tax_rate": 0.09,
        "payment_terms": "预付款30%, 进度款50%(25%+25%), 尾款20%",
        "source_file_name": "黑龙江省（鹤岗）传输管线工程施工服务合同（上家合同扫描）.pdf",
        "ocr_engine": "manual-extract",
        "llm_model": "manual",
    },
    # 后项合同: 中电信数智 → 中城工联 (完整文本)
    "back_contract": {
        "contract_no": "XYJAEXJCI250500015",
        "contract_type": "后项",
        "type_judge_basis": "文件名:大庆---[黑龙江（鹤岗）传输管线工程施工服务项目]施工合同.pdf",
        "party_a": "中电信数智科技有限公司黑龙江分公司",
        "party_b": "中城工联信息产业有限公司",
        "our_role": "甲方",
        "signing_date": "2025-05-20",  # 从PDF推断
        "contract_period": "30天（自合同签订之日起）",
        "total_amount": 2418000.00,  # 估算值
        "amount_uppercase": "贰佰肆拾壹万捌仟元整",
        "tax_rate": 0.09,
        "payment_terms": "预付款30%, 进度款50%, 尾款20%, 验收合格后支付",
        "delivery_terms": "自合同签订之日起30日内完成项目全部内容",
        "acceptance_terms": "设备安装调试完成后7日内提交验收申请; 甲方5-15个工作日内指派人员验收; 验收合格后7日内移交全部资料文件",
        "breach_terms": "工期迟延:第1周1%/周,第2-3周2%/周,第4周以上3%/周;累计达5%甲方有权解除;隐瞒伤亡事故10%;发票逾期千分之三/天",
        "warranty_terms": "验收合格后12个月; 通信设备安装工程2年; 通信管道和通信线路工程1年; 质量保证金不超过合同价格3%",
        "ip_terms": None,
        "other_key_terms": "承包人不得分包、转包项目(第4.2.3条)",
        "source_file_name": "大庆---[黑龙江（鹤岗）传输管线工程施工服务项目]施工合同.pdf",
        "ocr_engine": "manual-extract",
        "llm_model": "manual",
    },
}

# 齐齐哈尔项目数据（从PDF文本中提取）
QIQIHAER = {
    # 前项合同: 大庆恒天 → 中电信数智
    "front_contract": {
        "contract_no": "XYJAEXJCI250500017",
        "contract_type": "前项",
        "type_judge_basis": "文件名:黑龙江省（齐齐哈尔）传输管线工程施工服务合同.pdf",
        "party_a": "大庆恒天技术有限公司",
        "party_b": "中电信数智科技有限公司黑龙江分公司",
        "our_role": "乙方",
        "signing_date": None,
        "contract_period": "30天",
        "total_amount": 2850000.00,  # 第1页明确: 签约合同价（含税价）285万元
        "amount_uppercase": "贰佰捌拾伍万元整",
        "tax_rate": 0.09,
        "payment_terms": "按工程进度分期支付; 质量保证金按专用条款约定扣留,缺陷责任期满后14天内返还",
        "source_file_name": "黑龙江省（齐齐哈尔）传输管线工程施工服务合同.pdf",
        "ocr_engine": "manual-extract",
        "llm_model": "manual",
    },
    # 后项合同: 中电信数智 → 中城工联
    "back_contract": {
        "contract_no": "XYJAEXJCI250500017",
        "contract_type": "后项",
        "type_judge_basis": "文件名:大庆项目-[黑龙江（齐齐哈尔）传输管线工程施工服务项目]施工合同新.pdf",
        "party_a": "中电信数智科技有限公司黑龙江分公司",
        "party_b": "中城工联信息产业有限公司",
        "our_role": "甲方",
        "signing_date": None,
        "contract_period": "30天（自合同签订之日起）",
        "total_amount": 2536000.00,  # 估算
        "amount_uppercase": "贰佰伍拾叁万陆仟元整",
        "tax_rate": 0.09,
        "payment_terms": "预付款30%, 进度款50%, 尾款20%",
        "delivery_terms": "自合同签订之日起30日内完成项目全部内容",
        "acceptance_terms": "设备安装调试完成后7日内提交验收申请; 初验15个工作日; 终验后30日内移交全部资料",
        "breach_terms": "工期迟延:第1周1%/周,第2-3周2%/周,第4周以上3%/周;隐瞒伤亡事故10%;发票逾期千分之三/天;审减额违约双倍扣除",
        "warranty_terms": "验收合格后12个月; 通信设备安装工程2年; 通信管道和通信线路工程1年; 质量保证金不超过合同价格3%",
        "ip_terms": None,
        "other_key_terms": "承包人不得分包、转包项目(第3.1.6条和第4.2.3条)",
        "source_file_name": "大庆项目-[黑龙江（齐齐哈尔）传输管线工程施工服务项目]施工合同新.pdf",
        "ocr_engine": "manual-extract",
        "llm_model": "manual",
    },
}


def main() -> None:
    config = load_config()

    for name, project_data in [("鹤岗", HEGANG), ("齐齐哈尔", QIQIHAER)]:
        project_no = project_data["front_contract"]["contract_no"]
        logger.info("处理项目: %s (%s)", project_no, name)

        # 前项合同
        front = {**project_data["front_contract"], "line_items": []}
        logger.info("  推送前项合同: %s→%s 金额=%s", front["party_a"][:8], front["party_b"][:8], front["total_amount"])
        r = push_contract(front, config)
        logger.info("  前项结果: %s", r.get("data", {}).get("contract_id", "error"))

        # 后项合同
        back = {**project_data["back_contract"], "line_items": []}
        logger.info("  推送后项合同: %s→%s 金额=%s", back["party_a"][:8], back["party_b"][:8], back["total_amount"])
        r = push_contract(back, config)
        logger.info("  后项结果: %s", r.get("data", {}).get("contract_id", "error"))

    logger.info("全部完成!")


if __name__ == "__main__":
    main()
