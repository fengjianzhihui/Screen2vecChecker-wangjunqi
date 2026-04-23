from __future__ import annotations

from pathlib import Path

from engine import HeuristicChecker
from formatter import format_markdown_table, format_text_report


def load_sample_text() -> str:
    sample_path = Path(__file__).parent / "sample_input.txt"
    return sample_path.read_text(encoding="utf-8")


def main() -> None:
    checker = HeuristicChecker()

    print("=== Screen2VecChecker Demo ===")
    print("1. 使用示例输入")
    print("2. 手动输入描述文本")
    choice = input("请选择模式（1/2）：").strip()

    if choice == "2":
        print("\n请输入 UI 描述文本，输入完成后按回车：")
        ui_text = input("> ").strip()
    else:
        ui_text = load_sample_text()

    issues = checker.run(ui_text)

    print("\n=== 文本报告 ===")
    print(format_text_report(issues))

    print("\n=== Markdown 表格 ===")
    print(format_markdown_table(issues))


if __name__ == "__main__":
    main()