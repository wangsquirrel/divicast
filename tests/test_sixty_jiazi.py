import pickle
import unittest
from dataclasses import FrozenInstanceError
from itertools import product

from divicast.birth_chart.birth import ZhuInfo
from divicast.entities.ganzhi import Dizhi, Nayin, SixtyJiazi, Tiangan
from divicast.entities.protocols import HasGanzhi


class TestSixtyJiazi(unittest.TestCase):
    def test_all_120_stem_branch_combinations_admit_exactly_sixty_values(self) -> None:
        admitted = set()
        for gan, zhi in product(Tiangan, Dizhi):
            with self.subTest(gan=gan, zhi=zhi):
                if gan.yinyang != zhi.yinyang:
                    with self.assertRaises(ValueError):
                        SixtyJiazi(gan, zhi)
                else:
                    value = SixtyJiazi(gan, zhi)
                    admitted.add(value)
                    self.assertEqual(value, SixtyJiazi.parse(str(value)))
                    self.assertIsInstance(value, HasGanzhi)
        self.assertEqual(60, len(admitted))

    def test_constructor_requires_domain_symbols(self) -> None:
        invalid = (
            ("甲", Dizhi.Zi),
            (Tiangan.Jia, "子"),
            (0, Dizhi.Zi),
            (Tiangan.Jia, 0),
            (False, Dizhi.Zi),
            (Tiangan.Jia, None),
            (Dizhi.Zi, Tiangan.Jia),
        )
        for gan, zhi in invalid:
            with self.subTest(gan=gan, zhi=zhi), self.assertRaises(TypeError):
                SixtyJiazi(gan, zhi)

    def test_equality_and_hashing_are_by_value(self) -> None:
        original = SixtyJiazi(Tiangan.Jia, Dizhi.Zi)
        equal = SixtyJiazi.parse("甲子")
        different = SixtyJiazi.parse("乙丑")
        self.assertIsNot(original, equal)
        self.assertEqual(original, equal)
        self.assertEqual(hash(original), hash(equal))
        self.assertNotEqual(original, different)
        self.assertNotEqual(original, (Tiangan.Jia, Dizhi.Zi))
        self.assertNotEqual(original, "甲子")
        self.assertEqual(2, len({original, equal, different}))
        self.assertEqual("甲子日", {original: "甲子日"}[equal])

    def test_fields_cannot_change_after_construction(self) -> None:
        value = SixtyJiazi.parse("甲子")
        lookup = {value: "saved"}
        for attribute, replacement in (("gan", Tiangan.Yi), ("zhi", Dizhi.Chou)):
            with self.subTest(attribute=attribute):
                with self.assertRaises(FrozenInstanceError):
                    setattr(value, attribute, replacement)
                with self.assertRaises(FrozenInstanceError):
                    delattr(value, attribute)
        self.assertFalse(hasattr(value, "__dict__"))
        self.assertEqual("saved", lookup[SixtyJiazi.parse("甲子")])

    def test_parse_rejects_malformed_or_impossible_pairs(self) -> None:
        for text in ("", "甲", "甲子丑", "甲子garbage", " 甲子", "甲子 ", "子甲", "甲甲", "xx", "甲丑"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                SixtyJiazi.parse(text)
        for value in (None, 0, True, b"ganzhi", ["甲", "子"]):
            with self.subTest(value=value), self.assertRaises(TypeError):
                SixtyJiazi.parse(value)

    def test_string_representation_and_pickle_round_trip(self) -> None:
        value = SixtyJiazi.parse("癸亥")
        self.assertEqual("癸亥", str(value))
        self.assertIn("SixtyJiazi(", repr(value))
        self.assertEqual(value, pickle.loads(pickle.dumps(value)))

    def test_nayin_and_kongwang_for_the_complete_sixty_day_cycle(self) -> None:
        expected_nayin = (
            Nayin.HaiZhongJin,
            Nayin.LuZhongHuo,
            Nayin.DaLinMu,
            Nayin.LuPangTu,
            Nayin.JianFengjin,
            Nayin.ShanTouHuo,
            Nayin.DongXiaShui,
            Nayin.ChengQiangTu,
            Nayin.BaiLajin,
            Nayin.YangLiuMu,
            Nayin.QuanZhongShui,
            Nayin.WuShangTu,
            Nayin.PiLiHuo,
            Nayin.SongBaiMu,
            Nayin.ChangLiuShui,
            Nayin.ShaZhongJin,
            Nayin.ShanXiaHuo,
            Nayin.PingDiMu,
            Nayin.BiShanTu,
            Nayin.JinBoJin,
            Nayin.FoDengHuo,
            Nayin.TianHeShui,
            Nayin.DaYiTu,
            Nayin.ChaiShanJin,
            Nayin.SangSongMu,
            Nayin.DaXiShui,
            Nayin.ShaZhongTu,
            Nayin.TianShangHuo,
            Nayin.ShiLiuMu,
            Nayin.DaHaiShui,
        )
        xun_kongwang = ("戌亥", "申酉", "午未", "辰巳", "寅卯", "子丑")
        for index in range(60):
            value = SixtyJiazi(Tiangan(index % 10), Dizhi(index % 12))
            with self.subTest(day=str(value)):
                self.assertIs(expected_nayin[index // 2], value.get_nayin())
                self.assertEqual(xun_kongwang[index // 10], "".join(map(str, value.get_kongwang())))

    def test_chart_pillar_reuses_a_validated_value(self) -> None:
        value = SixtyJiazi.parse("甲子")
        zhu = ZhuInfo(value, day_master=Tiangan.Jia, shensha=())
        self.assertIs(value, zhu.sixty_jiazi)
        self.assertIs(Tiangan.Jia, zhu.gan)
        self.assertIs(Dizhi.Zi, zhu.zhi)
        self.assertIs(Nayin.HaiZhongJin, zhu.nayin)
        self.assertEqual((Dizhi.Xu, Dizhi.Hai), zhu.kongwang)
        for invalid in ("甲子", "甲丑", (Tiangan.Jia, Dizhi.Zi), None):
            with self.subTest(value=invalid), self.assertRaises(TypeError):
                ZhuInfo(invalid, day_master=Tiangan.Jia, shensha=())

    def test_chart_pillar_cannot_override_its_ganzhi_or_derived_values(self) -> None:
        zhu = ZhuInfo(SixtyJiazi.parse("甲子"), day_master=Tiangan.Jia, shensha=())
        for name, replacement in (
            ("sixty_jiazi", SixtyJiazi.parse("乙丑")),
            ("gan", Tiangan.Yi),
            ("zhi", Dizhi.Chou),
            ("nayin", Nayin.LuZhongHuo),
            ("kongwang", (Dizhi.Zi, Dizhi.Chou)),
        ):
            with self.subTest(attribute=name):
                with self.assertRaises(AttributeError):
                    setattr(zhu, name, replacement)
                with self.assertRaises(AttributeError):
                    delattr(zhu, name)
