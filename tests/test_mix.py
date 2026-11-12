import unittest

from tyme4py import solar

from divicast.entities.ganzhi import Dizhi, Tiangan
from divicast.entities.misc import Gender
from divicast.entities.wuxing import YinYang


class TestMix(unittest.TestCase):
    def test_symbols_expose_their_own_yinyang_property(self):
        self.assertIs(Gender.Male.yinyang, YinYang.Yang)
        self.assertIs(Gender.Female.yinyang, YinYang.Yin)
        self.assertIs(Tiangan.Jia.yinyang, YinYang.Yang)
        self.assertIs(Dizhi.Chou.yinyang, YinYang.Yin)


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
