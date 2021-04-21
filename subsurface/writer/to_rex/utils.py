import numpy as np


__all__ = ['hex_to_rgb', ]


def hex_to_rgb(hex: str, normalize: bool = True) -> np.ndarray:
    """Transform colors from hex to rgb"""
    hex = hex.lstrip('#')
    hlen = len(hex)
    rgb = np.array(
        [int(hex[i:i + hlen // 3], 16) for i in range(0, hlen, hlen // 3)])
    if normalize is True:
        rgb = rgb / 255
    return rgb
