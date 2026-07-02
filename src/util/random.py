"""随机采样工具。

当前文件只提供简单的伯努利采样辅助函数。
"""

import random


def binary_bernoulli_sample(p: float) -> bool:
    """按给定概率返回一次布尔采样结果。"""
    return random.uniform(0, 1) <= p
