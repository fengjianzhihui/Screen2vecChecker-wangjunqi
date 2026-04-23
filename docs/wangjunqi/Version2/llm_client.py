from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from rules import Rule


class DeepSeekLLMClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ) -> None:
        load_dotenv()

        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "sk-api")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.timeout = timeout

        self.enabled = bool(self.api_key.strip())
        self.client: Optional[OpenAI] = None

        if self.enabled:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )

    def is_available(self) -> bool:
        return self.enabled and self.client is not None

    def _build_system_prompt(self, rules: List[Rule]) -> str:
        rule_lines = []
        for r in rules:
            rule_lines.append(
                f"- {r.rule_id} | {r.rule_name} | 分类:{r.category} | 说明:{r.description} | "
                f"检查点:{'、'.join(r.check_points)} | 风险模板:{r.risk_template} | 建议模板:{r.advice_template}"
            )

        rules_text = "\n".join(rule_lines)

        return f"""
你是一个资深 UI/UX 可用性评审专家。你的任务是根据给定的 UI 描述文本，
严格按照启发式评价规则进行检查，输出结构化 JSON。

要求：
1. 只输出 JSON，不要输出额外解释。
2. 如果没有明显问题，issues 返回空数组。
3. 你要基于语义理解，不要只看关键词。
4. 严重度只能是：高 / 中 / 低
5. category、rule_name、description、risk、suggestion 要尽量与规则库一致
6. evidence 必须引用输入描述中的具体现象，不要空泛
7. 输出 JSON 格式如下：

{{
  "issues": [
    {{
      "rule_id": "H-01",
      "rule_name": "系统状态可见性",
      "category": "反馈不足",
      "description": "系统应及时向用户反馈当前状态与操作结果。",
      "severity": "高",
      "evidence": "点击提交后未描述加载状态、成功提示或失败反馈。",
      "risk": "用户无法确认操作是否生效，容易产生重复点击、等待焦虑或流程中断。",
      "suggestion": "增加按钮点击后的状态反馈、加载提示、成功/失败提示和过程说明。"
    }}
  ]
}}

可用规则库如下：
{rules_text}
""".strip()

    def _build_user_prompt(self, ui_text: str) -> str:
        return f"""
请对下面这段 UI 描述做启发式检查，并输出 json：

UI 描述：
{ui_text}
""".strip()

    def analyze_ui(self, ui_text: str, rules: List[Rule]) -> List[Dict[str, Any]]:
        if not self.is_available():
            raise RuntimeError("DeepSeek API 未配置。请设置环境变量 DEEPSEEK_API_KEY。")

        system_prompt = self._build_system_prompt(rules)
        user_prompt = self._build_user_prompt(ui_text)

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )

        content = response.choices[0].message.content
        if not content:
            return []

        data = json.loads(content)
        issues = data.get("issues", [])

        if not isinstance(issues, list):
            raise ValueError("LLM 返回格式错误：issues 不是列表。")

        normalized: List[Dict[str, Any]] = []
        for item in issues:
            normalized.append(
                {
                    "rule_id": str(item.get("rule_id", "")).strip() or "UNKNOWN",
                    "rule_name": str(item.get("rule_name", "")).strip() or "未知规则",
                    "category": str(item.get("category", "")).strip() or "一般可用性问题",
                    "description": str(item.get("description", "")).strip(),
                    "severity": str(item.get("severity", "中")).strip() or "中",
                    "evidence": str(item.get("evidence", "")).strip(),
                    "risk": str(item.get("risk", "")).strip(),
                    "suggestion": str(item.get("suggestion", "")).strip(),
                }
            )

        return normalized