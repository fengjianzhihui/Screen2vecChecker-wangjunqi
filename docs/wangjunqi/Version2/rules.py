from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    rule_id: str
    rule_name: str
    category: str
    description: str
    check_points: List[str]
    risk_template: str
    advice_template: str
    severity_hint: str = "中"


def get_default_rules() -> list[Rule]:
    return [
        Rule(
            rule_id="H-01",
            rule_name="系统状态可见性",
            category="反馈不足",
            description="系统应及时向用户反馈当前状态与操作结果。",
            check_points=["反馈", "提示", "加载", "成功", "失败", "状态", "进度"],
            risk_template="用户无法确认操作是否生效，容易产生重复点击、等待焦虑或流程中断。",
            advice_template="增加按钮点击后的状态反馈、加载提示、成功/失败提示和过程说明。",
            severity_hint="高",
        ),
        Rule(
            rule_id="H-02",
            rule_name="一致性与标准",
            category="设计不一致",
            description="界面中的命名、样式、交互方式应保持一致。",
            check_points=["一致", "统一", "相同", "规范"],
            risk_template="用户需要额外学习不同页面或控件的使用方式，增加理解成本。",
            advice_template="统一按钮命名、信息层级、页面跳转逻辑与交互样式。",
            severity_hint="中",
        ),
        Rule(
            rule_id="H-03",
            rule_name="错误预防",
            category="错误预防不足",
            description="系统应尽量预防错误，而不是只在出错后提示。",
            check_points=["校验", "限制", "确认", "必填", "禁用", "预防"],
            risk_template="用户可能在缺少约束的情况下提交错误信息，导致任务失败或数据污染。",
            advice_template="增加输入校验、危险操作确认、默认值约束与防误触机制。",
            severity_hint="高",
        ),
        Rule(
            rule_id="H-04",
            rule_name="用户控制与自由",
            category="可撤销性不足",
            description="用户应能方便返回、撤销或退出当前操作。",
            check_points=["返回", "取消", "撤销", "关闭", "退出"],
            risk_template="用户一旦进入错误流程或误操作后难以恢复，挫败感增强。",
            advice_template="提供清晰的返回路径、取消按钮、撤销入口和中断机制。",
            severity_hint="高",
        ),
        Rule(
            rule_id="H-05",
            rule_name="识别而非记忆",
            category="记忆负担过重",
            description="界面应减少用户记忆负担，让关键信息可见。",
            check_points=["示例", "占位", "默认值", "提示文案", "选项可见"],
            risk_template="用户需要记忆格式、步骤或状态，容易造成输入错误和理解困难。",
            advice_template="增加占位提示、示例文本、可见选项和上下文说明，减少记忆负担。",
            severity_hint="中",
        ),
        Rule(
            rule_id="H-06",
            rule_name="帮助用户识别、诊断并恢复错误",
            category="错误恢复支持不足",
            description="当错误发生时，系统应给出明确、可操作的修复建议。",
            check_points=["错误提示", "原因", "解决", "重试", "修复"],
            risk_template="用户即使意识到出错，也无法快速定位原因并完成恢复。",
            advice_template="让错误提示包含错误原因、影响范围和下一步操作建议。",
            severity_hint="高",
        ),
        Rule(
            rule_id="H-07",
            rule_name="界面简洁与信息最小化",
            category="信息冗余",
            description="界面应避免无关信息干扰，突出主要任务。",
            check_points=["简洁", "重点", "主按钮", "分组", "层级"],
            risk_template="界面噪音过多会分散用户注意力，降低任务完成效率。",
            advice_template="减少冗余元素，突出主任务路径，优化信息层级和视觉重点。",
            severity_hint="中",
        ),
    ]