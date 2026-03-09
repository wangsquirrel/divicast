from __future__ import annotations

import unittest

from divicast.base.symbol import ValuedMultiton


class YinYang(ValuedMultiton):
    """
    阴阳
    """

    Yin = (0, "阴")
    Yang = (1, "阳")


class Gender(ValuedMultiton):
    """
    性别
    """

    Male = (0, "男")
    Female = (1, "女")


Gender._BELONGS_TO = {YinYang: {Gender.Male: YinYang.Yang, Gender.Female: YinYang.Yin}}


class EOrI(ValuedMultiton):
    E = (0, "E")
    I = (1, "I")

EOrI._BELONGS_TO = {YinYang: lambda x: YinYang(x.num % 2)}


class TestMix(unittest.TestCase):
    def test_mix(self):
        self.assertEqual(Gender.Male.belongs_to(YinYang), YinYang.Yang)
        self.assertEqual(Gender.Female.belongs_to(YinYang), YinYang.Yin)
        self.assertEqual(EOrI.E.belongs_to(YinYang), YinYang.Yin)
        self.assertEqual(EOrI.I.belongs_to(YinYang), YinYang.Yang)
