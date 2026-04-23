from __future__ import annotations

from typing import Tuple

def validate_input(ui_text: str) -> Tuple[bool, str]:

    if not ui_text or not ui_text.strip():

        return False, "输入为空，请粘贴 Screen2Vec 生成的 UI 描述文本。"

    text = ui_text.strip()

    if len(text) < 20:

        return False, "输入内容过短，建议补充页面元素、交互动作和反馈信息。"

    keywords = ["页面", "按钮", "输入框", "文本", "提示", "反馈", "点击", "提交"]

    hit_count = sum(1 for k in keywords if k in text)

    if hit_count < 2:

        return False, "输入结构不完整，缺少界面元素或交互反馈描述。"

    return True, "ok"