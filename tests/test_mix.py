from __future__ import annotations

import unittest

from tyme4py import AbstractTyme, eightchar, enums, lunar, sixtycycle, solar  # type: ignore

from divicast.base.symbol import ValuedMultiton


class YinYang(ValuedMultiton):
    """
    阴阳
    """

    Yin = (0, "阴")
    Yang = (1, "阳")


class GenderExample(ValuedMultiton):
    """
    性别
    """

    Female = (0, "女")
    Male = (1, "男")


GenderExample._BELONGS_TO = {YinYang: {GenderExample.Male: YinYang.Yang, GenderExample.Female: YinYang.Yin}}


class EOrI(ValuedMultiton):
    E = (0, "E")
    I = (1, "I")


EOrI._BELONGS_TO = {YinYang: lambda x: YinYang(x.num % 2)}


class TestMix(unittest.TestCase):
    def test_mix(self):
        self.assertEqual(GenderExample.Male.belongs_to(YinYang), YinYang.Yang)
        self.assertEqual(GenderExample.Female.belongs_to(YinYang), YinYang.Yin)
        self.assertEqual(EOrI.E.belongs_to(YinYang), YinYang.Yin)
        self.assertEqual(EOrI.I.belongs_to(YinYang), YinYang.Yang)


class TestExtractLunar(unittest.TestCase):
    def test_extract_lunar_year(self):
        a = solar.SolarTime.from_ymd_hms(1993, 1, 22, 12, 0, 0)
        b = solar.SolarTime.from_ymd_hms(1993, 1, 23, 12, 0, 0)
        self.assertEqual(1992, a.get_solar_day().get_lunar_day().get_year())

        self.assertEqual(1993, b.get_solar_day().get_lunar_day().get_year())

    def test_extract_lunar_month(self):
        a = solar.SolarTime.from_ymd_hms(1993, 1, 22, 12, 0, 0)
        b = solar.SolarTime.from_ymd_hms(1993, 1, 23, 12, 0, 0)
        self.assertEqual(12, a.get_solar_day().get_lunar_day().get_month())

        self.assertEqual(1, b.get_solar_day().get_lunar_day().get_month())
        self.assertEqual(1, b.get_solar_day().get_lunar_day().get_month())
