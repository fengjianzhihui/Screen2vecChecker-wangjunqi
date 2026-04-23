from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from formatter import sort_issues
from rules import Rule, get_default_rules
from validator import validate_input


CATEGORY_MAP = {
    "系统状态可见性": "反馈不足",
    "一致性与标准": "设计不一致",
    "错误预防": "错误预防不足",
    "用户控制与自由": "可撤销性不足",
    "识别而非记忆": "记忆负担过重",
    "帮助用户识别、诊断并恢复错误": "错误恢复支持不足",
    "界面简洁与信息最小化": "信息冗余",
}


class HeuristicChecker:
    def __init__(self, rules: List[Rule] | None = None) -> None:
        self.rules = rules or get_default_rules()

    def infer_category(self, rule_name: str) -> str:
        return CATEGORY_MAP.get(rule_name, "一般可用性问题")

    def score_severity(self, rule: Rule, evidence: str) -> str:
        if rule.severity_hint in {"高", "中", "低"}:
            return rule.severity_hint

        if "错误" in evidence or "缺少反馈" in evidence:
            return "高"
        if "不一致" in evidence:
            return "中"
        return "低"

    def build_issue(self, rule: Rule, evidence: str) -> Dict:
        return {
            "rule_id": rule.rule_id,
            "rule_name": rule.rule_name,
            "category": self.infer_category(rule.rule_name),
            "description": rule.description,
            "severity": self.score_severity(rule, evidence),
            "evidence": evidence,
            "risk": rule.risk_template,
            "suggestion": rule.advice_template,
        }

    def check_rule_hit(self, ui_text: str, rule: Rule) -> bool:
        text = ui_text.strip()
        return any(point in text for point in rule.check_points)

    def run(self, ui_text: str) -> List[Dict]:
        ok, msg = validate_input(ui_text)
        if not ok:
            return [
                {
                    "rule_id": "INPUT-ERROR",
                    "rule_name": "输入校验",
                    "category": "输入异常",
                    "description": "在执行启发式规则分析前，先确保输入文本有效。",
                    "severity": "高",
                    "evidence": msg,
                    "risk": "无效输入会导致分析结论不稳定，影响结果可信度。",
                    "suggestion": "补充页面元素、交互动作和反馈信息后重新检查。",
                }
            ]

        issues: List[Dict] = []

        for rule in self.rules:
            hit = self.check_rule_hit(ui_text, rule)
            if not hit:
                evidence = f"描述中缺少与“{rule.rule_name}”相关的信息，当前文本未体现关键检查点：{', '.join(rule.check_points[:3])}。"
                issues.append(self.build_issue(rule, evidence))

        return sort_issues(issues)

    def export_rules(self) -> List[Dict]:
        return [asdict(rule) for rule in self.rules]