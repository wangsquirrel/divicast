from __future__ import annotations

from typing import ClassVar, Dict, List

from divicast.base.symbol import ValuedMultiton
from divicast.entities.wuxing import *
from divicast.entities.wuxing import Wuxing


class Line(ValuedMultiton):
    """
    爻
    """

    YinYao = (0, "⚋")
    YangYao = (1, "⚊")


class Trigram(BelongsToWuxing, ValuedMultiton):
    """
    八卦
    """
    _WUXING_MAP: ClassVar[Dict[Trigram, Wuxing]]
    _PRIMARY_IMAGE_MAP: ClassVar[Dict[Trigram, str]]
    lines: List[Line]

    Kun = (0, "坤")
    Zhen = (1, "震")
    Kan = (2, "坎")
    Dui = (3, "兑")
    Gen = (4, "艮")
    Li = (5, "离")
    Xun = (6, "巽")
    Qian = (7, "乾")

    def __init__(self, num: int, chinese_name: str | None = None):
        """
        :param num: 0-7
        :param name: 可选, 如果不提供则使用类名
        :param chinese_name: 可选, 如果不提供则使用类名
        """
        ValuedMultiton.__init__(self, num, chinese_name)
        self.lines = [Line((num >> 0) & 1), Line(
            (num >> 1) & 1), Line((num >> 2) & 1)]

    @property
    def primary_image(self) -> str:
        """
        主象
        """
        return self._PRIMARY_IMAGE_MAP[self]


Trigram._WUXING_MAP = {
    Trigram.Qian: Wuxing.Metal,
    Trigram.Dui: Wuxing.Metal,
    Trigram.Kan: Wuxing.Water,
    Trigram.Gen: Wuxing.Earth,
    Trigram.Li: Wuxing.Fire,
    Trigram.Xun: Wuxing.Wood,
    Trigram.Zhen: Wuxing.Wood,
    Trigram.Kun: Wuxing.Earth,
}
Trigram._PRIMARY_IMAGE_MAP = {
    Trigram.Qian: '天',
    Trigram.Dui: '泽',
    Trigram.Kan: '水',
    Trigram.Gen: '山',
    Trigram.Li: '火',
    Trigram.Xun: '风',
    Trigram.Zhen: '雷',
    Trigram.Kun: '地'
}


class Hexagram(ValuedMultiton):
    """六十四卦"""

    H63 = (63, "乾")
    H0 = (0, "坤")
    H17 = (17, "屯")
    H34 = (34, "蒙")
    H23 = (23, "需")
    H58 = (58, "讼")
    H2 = (2, "师")
    H16 = (16, "比")
    H55 = (55, "小畜")
    H59 = (59, "履")
    H7 = (7, "泰")
    H56 = (56, "否")
    H61 = (61, "同人")
    H47 = (47, "大有")
    H4 = (4, "谦")
    H8 = (8, "豫")
    H25 = (25, "随")
    H38 = (38, "蛊")
    H3 = (3, "临")
    H48 = (48, "观")
    H41 = (41, "噬嗑")
    H37 = (37, "贲")
    H32 = (32, "剥")
    H1 = (1, "复")
    H57 = (57, "无妄")
    H39 = (39, "大畜")
    H33 = (33, "颐")
    H30 = (30, "大过")
    H18 = (18, "坎")
    H45 = (45, "离")
    H28 = (28, "咸")
    H14 = (14, "恒")
    H60 = (60, "遁")
    H15 = (15, "大壮")
    H40 = (40, "晋")
    H5 = (5, "明夷")
    H53 = (53, "家人")
    H43 = (43, "睽")
    H20 = (20, "蹇")
    H10 = (10, "解")
    H35 = (35, "损")
    H49 = (49, "益")
    H31 = (31, "夬")
    H62 = (62, "姤")
    H24 = (24, "萃")
    H6 = (6, "升")
    H26 = (26, "困")
    H22 = (22, "井")
    H29 = (29, "革")
    H46 = (46, "鼎")
    H9 = (9, "震")
    H36 = (36, "艮")
    H52 = (52, "渐")
    H11 = (11, "归妹")
    H13 = (13, "丰")
    H44 = (44, "旅")
    H54 = (54, "巽")
    H27 = (27, "兑")
    H50 = (50, "涣")
    H19 = (19, "节")
    H51 = (51, "中孚")
    H12 = (12, "小过")
    H21 = (21, "既济")
    H42 = (42, "未济")

    def inside_trigram(self) -> Trigram:
        return Trigram(self.num % 8)

    def outside_trigram(self) -> Trigram:
        return Trigram(self.num // 8)

    def belongs_to_trigram(self) -> Trigram:
        """
        归宫
        """

        if self.belongs_to_trigram_seq() in [1, 2, 3, 6]:  # 一二三六外卦宫
            return self.outside_trigram()
        elif self.belongs_to_trigram_seq() in [4, 5, 7]:  # 四五游魂内变更
            return Trigram(self.inside_trigram().num ^ 0b111)
        elif self.belongs_to_trigram_seq() == 8:  # 归魂内卦是本宫
            return self.inside_trigram()
        else:
            raise AssertionError("Unexpected belongs_to_trigram_seq")

    def belongs_to_trigram_seq(self) -> int:
        """
        归宫的序号
        CAVEAT: 这里的序号是从1开始的, 方便口诀计算
        """

        _0 = (self.num & 0b000001) ^ ((self.num & 0b001000) >> 3) == 0  # 地
        _1 = (self.num & 0b000010) ^ ((self.num & 0b010000) >> 3) == 0  # 人
        _2 = (self.num & 0b000100) ^ ((self.num & 0b100000) >> 3) == 0  # 天
        seq = 0

        if _2 and not _1 and not _0:  # 天同二世
            seq = 2
        elif not _2 and _1 and _0:  # 天变五
            seq = 5
        elif not _2 and not _1 and _0:  # 地同四世
            seq = 4
        elif _2 and _1 and not _0:  # 地变一
            seq = 1
        elif _2 and _1 and _0:  # 本宫六世
            seq = 6
        elif not _2 and not _1 and not _0:  # 三世异
            seq = 3
        elif not _2 and _1 and not _0:  # 人同游魂
            seq = 7  # 游魂
        elif _2 and not _1 and _0:  # 人变归
            seq = 8  # 归魂
        else:
            raise ValueError("无法判断归宫的序号")
        return seq
