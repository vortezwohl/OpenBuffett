"""章节切分工具。

该文件负责按中文或英文章节标题模式拆分长文本。
"""

import re

ZH_PATTERN = r'\s*第\s*\d+|[一二三四五六七八九十零百千万]+\s*章\s*(.*)'
EN_PATTERN = r'\s*Chapter\s*(.*)\d+\s'


def split_content(text: str, pattern: str = ZH_PATTERN) -> list[str]:
    """按章节标题模式把全文拆分为章节列表。"""
    chapters = list[str]()
    pattern = re.compile(f'({pattern})')
    matches = pattern.findall(text)
    try:
        for i, (title, content) in enumerate(matches[::-1]):
            match_pos = text.rfind(title)
            chapters.append(f'{title}\n\n{text[match_pos + len(title):].strip()}')
            text = text[:match_pos]
    except ValueError:
        for i, title in enumerate(matches[::-1]):
            match_pos = text.rfind(title)
            chapters.append(f'{title}\n\n{text[match_pos + len(title):].strip()}')
            text = text[:match_pos]
    return chapters[::-1]
