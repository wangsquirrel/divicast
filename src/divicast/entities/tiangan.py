from __future__ import annotations  # 用于前向引用

from typing import Self

from divicast.base.symbol import ValuedMultiton
from divicast.entities.ganzhi import Dizhi, TwelveZhangsheng
from divicast.entities.wuxing import Wuxing, YinYang


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


class Tiangan(ValuedMultiton):
    """
    天干
    """

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

    def get_shishen(self, other: Self) -> Shishen:
        """
        获取对应的十神
        """
        if self.belongs_to(Wuxing) == other.belongs_to(Wuxing):
            # 同五行
            return (
                Shishen.BiJian
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.JieCai  # type: ignore
            )
        elif self.belongs_to(Wuxing).generate() == other.belongs_to(Wuxing):
            # 我生对方
            return (
                Shishen.ShiShen
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.ShangGuan  # type: ignore
            )
        elif self.belongs_to(Wuxing).restrain() == other.belongs_to(Wuxing):
            # 我克对方
            return (
                Shishen.PianCai
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.ZhengCai  # type: ignore
            )
        elif self.belongs_to(Wuxing) == other.belongs_to(Wuxing).restrain():
            # 对方克我
            return (
                Shishen.QiSha
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.ZhengGuan  # type: ignore
            )
        elif self.belongs_to(Wuxing) == other.belongs_to(Wuxing).generate():
            # 对方生我
            return (
                Shishen.PianYin
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.ZhengYin  # type: ignore
            )
        else:
            raise ValueError("无法计算对应的十神关系")

    def get_twelve_zhangsheng(self, zhi: Dizhi) -> TwelveZhangsheng:
        """
        获取对应的十二长生
        """
        CHANGSHENG_START_BRANCH = {
            0: 11,  # 甲 in 亥
            1: 6,  # 乙 in 午
            2: 2,  # 丙 in 寅
            3: 9,  # 丁 in 酉
            4: 2,  # 戊 in 寅
            5: 9,  # 己 in 酉
            6: 5,  # 庚 in 巳
            7: 0,  # 辛 in 子
            8: 8,  # 壬 in 申
            9: 3,  # 癸 in 卯
        }
        start_branch_index = CHANGSHENG_START_BRANCH[self.num]
        if self.belongs_to(YinYang) == YinYang.Yang:
            # 阳干顺行
            changsheng_index = (zhi.num - start_branch_index + 12) % 12
        else:
            # 阴干逆行
            changsheng_index = (start_branch_index - zhi.num + 12) % 12

        return TwelveZhangsheng(changsheng_index)


Tiangan._BELONGS_TO = {
    Wuxing: {
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
    },
    YinYang: lambda x: YinYang((x.num + 1) % 2),
}
