"""字符串处理工具。

该文件提供子串定位、行号标注以及数值抽取等常用字符串辅助函数。
"""

import re


def find_substring_range(main_str: str, sub_str: str) -> tuple[int, int]:
    """返回子串在主串中的起止字符下标。"""
    main_str, sub_str = main_str.strip(), sub_str.strip()
    start_index = main_str.find(sub_str)
    if start_index != -1:
        end_index = start_index + len(sub_str) - 1
    else:
        end_index = -1
    return start_index, end_index


def find_substring_range_by_line(main_str: str, sub_str: str) -> tuple[int, int]:
    """返回子串在主串中对应的行号范围。"""
    main_str, sub_str = main_str.strip(), sub_str.strip()
    start_idx, end_idx = find_substring_range(main_str, sub_str)
    text_before = main_str[:start_idx]
    lines_before = len(text_before.splitlines(keepends=False))
    lines_selected = len(sub_str.splitlines(keepends=False))
    line_range_selected = (lines_before - 1, lines_before + lines_selected - 1)
    return line_range_selected


def squeeze_lines(text: str) -> str:
    """压缩多余空行并去除每行两端空白。"""
    text = text.strip()
    return '\n'.join([
        x.strip()
        for x in text.splitlines(keepends=False)
        if x not in ('\n', '\r', '')
    ])


def line_number_annotate(
    text: str,
    simplify: bool = False,
    bypass_pattern: str = '',
) -> str:
    """为文本逐行添加行号，可选择跳过特定匹配行。"""
    bypass_pattern = re.compile(bypass_pattern) if len(bypass_pattern) > 0 else None
    raw_lines = squeeze_lines(text).splitlines(keepends=False)
    lines = []
    _line_counter = 1
    for _l in raw_lines:
        if bypass_pattern is not None and bypass_pattern.fullmatch(_l):
            lines.append(_l)
            continue
        lines.append(
            f'line {_line_counter}. {_l}'
            if not simplify
            else f'{_line_counter}. {_l}'
        )
        _line_counter += 1
    return '\n'.join(lines)


def extract_integers(text: str) -> list[int]:
    """从文本中提取所有整数。"""
    return [int(x) for x in re.findall(r"\d+", text)]


def extract_floats(text: str) -> list[float]:
    """从文本中提取所有浮点或整数形式的数值。"""
    return [
        float(x)
        for x in re.findall(
            r"(?<![\w.])[+-]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?![\w.])",
            text,
        )
    ]
