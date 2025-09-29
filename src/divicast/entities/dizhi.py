from __future__ import annotations  # 用于前向引用

from typing import ClassVar, Dict, List

from divicast.base.symbol import ValuedMultiton
from divicast.entities.wuxing import *


class Dizhi(BelongsToYinYang, BelongsToWuxing, ValuedMultiton):
    """
    地支
    """

    _WUXING_MAP: Dict['Dizhi', 'Wuxing']

    Zi = (0, "子")
    Chou = (1, "丑")
    Yin = (2, "寅")
    Mou = (3, "卯")
    Chen = (4, "辰")
    Si = (5, "巳")
    Wu = (6, "午")
    Wei = (7, "未")
    Shen = (8, "申")
    You = (9, "酉")
    Xu = (10, "戌")
    Hai = (11, "亥")

    def is_chong(self, d: Dizhi) -> bool:
        """判断地支相冲"""
        return abs(self.num - d.num) == 6

    def chong(self) -> Dizhi:
        """返回相冲的地支"""
        return Dizhi((self.num + 6) % 12)

    def is_he(self, d: Dizhi) -> bool:
        """判断地支相合"""
        return (self.num + d.num) % 12 == 1

    def he(self) -> Dizhi:
        """返回相合的地支"""
        return Dizhi((13 - self.num) % 12)

    def belongs_to_yinyang(self) -> YinYang:
        return YinYang((self.num+1) % 2)

    def generate(self) -> List[Dizhi]:
        r = []
        w = self.belongs_to_wuxing().generate()
        for d in self.all():
            if d.belongs_to_wuxing() == w:
                r.append(d)
        return r

    def restrain(self) -> List[Dizhi]:
        r = []
        w = self.belongs_to_wuxing().restrain()
        for d in self.all():
            if d.belongs_to_wuxing() == w:
                r.append(d)
        return r


Dizhi._WUXING_MAP = {
    Dizhi.Zi: Wuxing.Water,
    Dizhi.Chou: Wuxing.Earth,
    Dizhi.Yin: Wuxing.Wood,
    Dizhi.Mou: Wuxing.Wood,
    Dizhi.Chen: Wuxing.Earth,
    Dizhi.Si: Wuxing.Fire,
    Dizhi.Wu: Wuxing.Fire,
    Dizhi.Wei: Wuxing.Earth,
    Dizhi.Shen: Wuxing.Metal,
    Dizhi.You: Wuxing.Metal,
    Dizhi.Xu: Wuxing.Earth,
    Dizhi.Hai: Wuxing.Water,
}
