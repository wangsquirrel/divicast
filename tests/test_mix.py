from __future__ import annotations

import unittest
from typing import ClassVar, Dict

from divicast.base.symbol import BelongsTo, ValuedMultiton


class YinYang(ValuedMultiton):
    """
    阴阳
    """

    Yin = (0, "阴")
    Yang = (1, "阳")


class BelongsToYinYang(BelongsTo):

    def belongs_to_yinyang(self) -> YinYang:
        return self.belongs_to(YinYang, "_YINYANG_MAP")


class Gender(BelongsToYinYang, ValuedMultiton):
    """
    性别
    """
    _YINYANG_MAP: ClassVar[Dict[Gender, YinYang]]

    Male = (0, "男")
    Female = (1, "女")


Gender._YINYANG_MAP = {
    Gender.Male: YinYang.Yang,
    Gender.Female: YinYang.Yin,
}


class EOrI(BelongsToYinYang, ValuedMultiton):
    E = (0, "E")
    I = (1, "I")

    # 覆盖默认实现
    def belongs_to_yinyang(self) -> YinYang:
        return YinYang(self.num % 2)


class TestMix(unittest.TestCase):
    def test_mix(self):
        self.assertEqual(Gender.Male.belongs_to_yinyang(), YinYang.Yang)
        self.assertEqual(Gender.Female.belongs_to_yinyang(), YinYang.Yin)
        self.assertEqual(EOrI.E.belongs_to_yinyang(), YinYang.Yin)
        self.assertEqual(EOrI.I.belongs_to_yinyang(), YinYang.Yang)
