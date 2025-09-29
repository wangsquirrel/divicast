from __future__ import annotations  # 用于前向引用

from typing import ClassVar, Dict, Self

from divicast.base.symbol import ValuedMultiton
from divicast.entities.wuxing import (BelongsToWuxing, BelongsToYinYang,
                                      Wuxing, YinYang)


class Shishen(ValuedMultiton):
    """
    十神
    """

    BiJian = (0, "比肩")
    JieCai = (1, "劫财")
    ShiShen = (2, "食神")
    ShangGuan = (3, "伤官")
    PianCai = (4, "偏财")
    ZhengCai = (5, "正财")
    QiSha = (6, "七杀")  # 也叫偏官
    ZhengGuan = (7, "正官")
    PianYin = (8, "偏印")  # 也叫枭神
    ZhengYin = (9, "正印")


class Tiangan(BelongsToWuxing, BelongsToYinYang, ValuedMultiton):
    """
    天干
    """
    _WUXING_MAP: ClassVar[Dict[Tiangan, Wuxing]]

    Jia = (0, "甲")
    Yi = (1, "乙")
    Bing = (2, "丙")
    Ding = (3, "丁")
    Wu = (4, "戊")
    Ji = (5, "己")
    Geng = (6, "庚")
    Xin = (7, "辛")
    Ren = (8, "壬")
    Gui = (9, "癸")

    def belongs_to_yinyang(self) -> YinYang:
        """
        获取天干所属的阴阳
        """
        return YinYang((self.num+1) % 2)

    def get_shishen(self, other: Self) -> Shishen:
        """
        获取对应的十神
        """
        if self.belongs_to_wuxing() == other.belongs_to_wuxing():
            # 同五行
            return (
                Shishen.BiJian
                if self.belongs_to_yinyang() == other.belongs_to_yinyang()
                else Shishen.JieCai  # type: ignore
            )
        elif self.belongs_to_wuxing().generate() == other.belongs_to_wuxing():
            # 我生对方
            return (
                Shishen.ShiShen
                if self.belongs_to_yinyang() == other.belongs_to_yinyang()
                else Shishen.ShangGuan  # type: ignore
            )
        elif self.belongs_to_wuxing().restrain() == other.belongs_to_wuxing():
            # 我克对方
            return (
                Shishen.PianCai
                if self.belongs_to_yinyang() == other.belongs_to_yinyang()
                else Shishen.ZhengCai  # type: ignore
            )
        elif self.belongs_to_wuxing() == other.belongs_to_wuxing().restrain():
            # 对方克我
            return (
                Shishen.QiSha
                if self.belongs_to_yinyang() == other.belongs_to_yinyang()
                else Shishen.ZhengGuan  # type: ignore
            )
        elif self.belongs_to_wuxing() == other.belongs_to_wuxing().generate():
            # 对方生我
            return (
                Shishen.PianYin
                if self.belongs_to_yinyang() == other.belongs_to_yinyang()
                else Shishen.ZhengYin  # type: ignore
            )
        else:
            raise ValueError("无法计算对应的十神关系")


Tiangan._WUXING_MAP = {
    Tiangan.Jia: Wuxing.Wood,
    Tiangan.Yi: Wuxing.Wood,
    Tiangan.Bing: Wuxing.Fire,
    Tiangan.Ding: Wuxing.Fire,
    Tiangan.Wu: Wuxing.Earth,
    Tiangan.Ji: Wuxing.Earth,
    Tiangan.Geng: Wuxing.Metal,
    Tiangan.Xin: Wuxing.Metal,
    Tiangan.Ren: Wuxing.Water,
    Tiangan.Gui: Wuxing.Water,
}
