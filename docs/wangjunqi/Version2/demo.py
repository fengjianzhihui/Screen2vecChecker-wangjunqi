from __future__ import annotations

from pathlib import Path

from engine import HeuristicChecker
from formatter import format_markdown_table, format_text_report


def load_sample_text() -> str:
    sample_path = Path(__file__).parent / "sample_input.txt"
    if sample_path.exists():
        return sample_path.read_text(encoding="utf-8")
    return (
        "这是一个注册页面。页面顶部有标题“创建账号”，中间有手机号输入框、"
        "验证码输入框、密码输入框。验证码按钮位于输入框右侧。底部有“注册”按钮和"
        "“已有账号，去登录”链接。页面未说明密码规则，也没有显示验证码有效时间。"
    )


def main() -> None:
    print("=== Screen2VecChecker Demo ===")
    print("1. 使用示例输入")
    print("2. 手动输入描述文本")
    choice = input("请选择模式（1/2）：").strip()

    if choice == "2":
        print("\n请输入 UI 描述文本，输入完成后按回车：")
        ui_text = input("> ").strip()
    else:
        ui_text = load_sample_text()

    print("\n请选择分析模式：")
    print("1. LLM 分析（已配置 API 时优先）")
    print("2. 仅规则分析")
    mode = input("请选择模式（1/2，默认1）：").strip()

    checker = HeuristicChecker(use_llm=(mode != "2"))
    issues = checker.run(ui_text)

    print("\n=== 文本报告 ===")
    print(format_text_report(issues))

    print("\n=== Markdown 表格 ===")
    print(format_markdown_table(issues))


if __name__ == "__main__":
    main()