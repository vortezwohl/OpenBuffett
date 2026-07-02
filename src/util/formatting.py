"""文本格式整理工具。

该文件提供从带思维链标记的输出中抽取正文、适配手机阅读排版以及
章节显示格式化的辅助函数。
"""


def cot_output_extractor(output: str, pattern: str) -> tuple[str, str]:
    """从带标记的模型输出中提取思维链与正文。"""
    pattern = pattern.lstrip('[').rstrip(']')
    cot = output[
        output.find('[COT]') + len('[COT]'): output.rfind(f'[{pattern}]')
    ].strip()
    content = output[output.rfind(f'[{pattern}]') + len(f'[{pattern}]'):].strip()
    cot = cot.lstrip('{{').rstrip('}}').lstrip('{').rstrip('}').strip()
    content = content.lstrip('{{').rstrip('}}').lstrip('{').rstrip('}').strip()
    return cot, content
