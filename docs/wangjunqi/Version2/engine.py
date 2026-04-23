from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from formatter import sort_issues
from llm_client import DeepSeekLLMClient
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
    def __init__(
        self,
        rules: List[Rule] | None = None,
        use_llm: bool = True,
    ) -> None:
        self.rules = rules or get_default_rules()
        self.use_llm = use_llm
        self.llm_client = DeepSeekLLMClient()

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

    def run_rule_based(self, ui_text: str) -> List[Dict]:
        issues: List[Dict] = []

        for rule in self.rules:
            hit = self.check_rule_hit(ui_text, rule)
            if not hit:
                evidence = (
                    f"描述中缺少与“{rule.rule_name}”相关的信息，"
                    f"当前文本未体现关键检查点：{', '.join(rule.check_points[:3])}。"
                )
                issues.append(self.build_issue(rule, evidence))

        return sort_issues(issues)

    def run_llm_based(self, ui_text: str) -> List[Dict]:
        issues = self.llm_client.analyze_ui(ui_text, self.rules)
        return sort_issues(issues)

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

        if self.use_llm and self.llm_client.is_available():
            try:
                print("[INFO] 当前使用 LLM 分析（DeepSeek）")
                llm_issues = self.run_llm_based(ui_text)
                return llm_issues
            except Exception as e:
                print(f"[WARN] LLM 调用失败，已回退到规则模式：{e}")
                fallback_issues = self.run_rule_based(ui_text)
                fallback_issues.insert(
                    0,
                    {
                        "rule_id": "LLM-FALLBACK",
                        "rule_name": "LLM 调用失败，已回退规则模式",
                        "category": "系统提示",
                        "description": "LLM 分析不可用时，系统会自动降级为规则检查。",
                        "severity": "中",
                        "evidence": str(e),
                        "risk": "结果的语义理解能力下降，可能产生误报或漏报。",
                        "suggestion": "检查 API Key、网络、模型名或返回格式。",
                    },
                )
                return sort_issues(fallback_issues)
        print("[INFO] 当前使用规则分析")
        return self.run_rule_based(ui_text)

    def export_rules(self) -> List[Dict]:
        return [asdict(rule) for rule in self.rules]