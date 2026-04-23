from __future__ import annotations

from typing import List, Dict


SEVERITY_ORDER = {"高": 0, "中": 1, "低": 2}


def sort_issues(issues: List[Dict]) -> List[Dict]:
    return sorted(issues, key=lambda x: SEVERITY_ORDER.get(x.get("severity", "低"), 3))


def format_text_report(issues: List[Dict]) -> str:
    if not issues:
        return "未发现明显问题。"

    lines: list[str] = []
    for idx, item in enumerate(issues, start=1):
        lines.append(
            f"{idx}. [{item.get('severity', '低')}] {item.get('category', '未分类')} - {item.get('rule_name', '未知规则')}\n"
            f"   规则依据：{item.get('description', '')}\n"
            f"   证据：{item.get('evidence', '')}\n"
            f"   风险：{item.get('risk', '')}\n"
            f"   建议：{item.get('suggestion', '')}"
        )
    return "\n".join(lines)


def format_markdown_table(issues: List[Dict]) -> str:
    if not issues:
        return "| 严重度 | 类别 | 规则 | 证据 | 风险 | 建议 |\n|---|---|---|---|---|---|\n| - | - | - | 未发现明显问题 | - | - |"

    header = "| 严重度 | 类别 | 规则 | 证据 | 风险 | 建议 |\n|---|---|---|---|---|---|"
    rows = []
    for item in issues:
        rows.append(
            f"| {item.get('severity', '')} | {item.get('category', '')} | {item.get('rule_name', '')} | "
            f"{item.get('evidence', '')} | {item.get('risk', '')} | {item.get('suggestion', '')} |"
        )
    return header + "\n" + "\n".join(rows)