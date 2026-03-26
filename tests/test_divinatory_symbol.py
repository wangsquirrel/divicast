import datetime
import json
import logging
import unittest

from jsonschema import validate

from divicast.entities import liushen
from divicast.entities.daemon import Daemon
from divicast.entities.ganzhi import Dizhi, Tiangan
from divicast.entities.relative import Relative
from divicast.entities.trigram import Hexagram, Trigram
from divicast.entities.wuxing import Wuxing
from divicast.sixline.divinatory_symbol import DivinatorySymbol
from divicast.sixline.output import StandardDivinatorySymbolOutput, to_standard_format


def expand(d, s):
    for i, e in enumerate(d[s]):
        d[s + str(i)] = e


class TestHexagram(unittest.TestCase):
    def test_liu_chong(self):
        # 六冲卦
        self.assertEqual(
            set(str(x) for x in Hexagram.all() if x.is_liuchong()),
            set(["乾", "坤", "坎", "离", "震", "艮", "兑", "巽", "大壮", "无妄"]),
        )
        self.assertFalse(Hexagram.H1.is_liuchong())


class TestDivinatorySymbol(unittest.TestCase):
    def test_variant_outside_trigram(self):
        d = DivinatorySymbol.create([1, 3, 0, 1, 0, 0], datetime.datetime(2024, 6, 11, 14, 5, 0))
        """
        青龙 父母 庚戌土 ⚋ × 应     父母 壬戌土 ⚊
        玄武 兄弟 庚申金 ⚋ ×        兄弟 壬申金 ⚊
        白虎 官鬼 庚午火 ⚊          官鬼 壬午火 ⚊
        (伏：子孙 丁亥水)
        腾蛇 父母 丁丑土 ⚋ × 世     子孙 己亥水 ⚊
        勾陈 妻财 丁卯木 ⚊ 〇       父母 己丑土 ⚋
        朱雀 官鬼 丁巳火 ⚊          妻财 己卯木 ⚊
        """
        self.assertEqual(str(d.bazi), "甲辰 庚午 丙午 乙未")
        self.assertEqual(str(d.kongwang[0]) + str(d.kongwang[1]), "寅卯")

        # 六神
        self.assertEqual(d.lines[0].liushen, liushen.Liushen(1))
        self.assertEqual(d.lines[1].liushen, liushen.Liushen(2))
        self.assertEqual(d.lines[2].liushen, liushen.Liushen(3))
        self.assertEqual(d.lines[3].liushen, liushen.Liushen(4))
        self.assertEqual(d.lines[4].liushen, liushen.Liushen(5))
        self.assertEqual(d.lines[5].liushen, liushen.Liushen(0))

        # 爻变
        self.assertEqual(d.lines[0].is_changed, False)
        self.assertEqual(d.lines[1].is_changed, True)
        self.assertEqual(d.lines[2].is_changed, True)
        self.assertEqual(d.lines[3].is_changed, False)
        self.assertEqual(d.lines[4].is_changed, True)
        self.assertEqual(d.lines[5].is_changed, True)

        # 世应
        self.assertFalse(d.lines[0].origin.is_subject)
        self.assertFalse(d.lines[1].origin.is_subject)
        self.assertTrue(d.lines[2].origin.is_subject)
        self.assertFalse(d.lines[3].origin.is_subject)
        self.assertFalse(d.lines[4].origin.is_subject)
        self.assertFalse(d.lines[5].origin.is_subject)

        self.assertFalse(d.lines[0].origin.is_object)
        self.assertFalse(d.lines[1].origin.is_object)
        self.assertFalse(d.lines[2].origin.is_object)
        self.assertFalse(d.lines[3].origin.is_object)
        self.assertFalse(d.lines[4].origin.is_object)
        self.assertTrue(d.lines[5].origin.is_object)
        self.assertEqual(
            [
                liushen.Liushen["朱雀"],
                liushen.Liushen["勾陈"],
                liushen.Liushen["腾蛇"],
                liushen.Liushen["白虎"],
                liushen.Liushen["玄武"],
                liushen.Liushen["青龙"],
            ],
            d.six_denties,
        )
        # 初爻
        self.assertEqual(d.lines[0].liushen, liushen.Liushen["朱雀"])
        self.assertEqual(d.lines[0].origin.relative, Relative["官鬼"])
        self.assertEqual(d.lines[0].origin.gan, Tiangan["丁"])
        self.assertEqual(d.lines[0].origin.zhi, Dizhi["巳"])
        self.assertEqual(d.lines[0].origin.wuxing, Wuxing["火"])
        self.assertIsNone(d.lines[0].variant.is_object)
        self.assertIsNone(d.lines[0].variant.is_subject)
        self.assertEqual(d.lines[0].variant.relative, Relative["妻财"])
        self.assertEqual(d.lines[0].variant.gan, Tiangan["己"])
        self.assertEqual(d.lines[0].variant.zhi, Dizhi["卯"])
        self.assertEqual(d.lines[0].variant.wuxing, Wuxing["木"])

        # 二爻
        self.assertEqual(d.lines[1].liushen, liushen.Liushen["勾陈"])
        self.assertEqual(d.lines[1].origin.relative, Relative["妻财"])
        self.assertEqual(d.lines[1].origin.gan, Tiangan["丁"])
        self.assertEqual(d.lines[1].origin.zhi, Dizhi["卯"])
        self.assertEqual(d.lines[1].origin.wuxing, Wuxing["木"])
        self.assertIsNone(d.lines[1].variant.is_object)
        self.assertIsNone(d.lines[1].variant.is_subject)
        self.assertEqual(d.lines[1].variant.relative, Relative["父母"])
        self.assertEqual(d.lines[1].variant.gan, Tiangan["己"])
        self.assertEqual(d.lines[1].variant.zhi, Dizhi["丑"])
        self.assertEqual(d.lines[1].variant.wuxing, Wuxing["土"])
        # 神煞
        self.assertEqual(d.daemons[Daemon.Tianyiguiren], [Dizhi.Hai, Dizhi.You])
        self.assertEqual(d.daemons[Daemon.Yima], [Dizhi.Shen])
        self.assertEqual(d.daemons[Daemon.Taohua], [Dizhi.Mou])
        self.assertEqual(d.daemons[Daemon.Wenchang], [Dizhi.Shen])
        self.assertEqual(d.daemons[Daemon.Lushen], [Dizhi.Si])
        self.assertEqual(d.daemons[Daemon.Jiesha], [Dizhi.Hai])
        self.assertEqual(d.daemons[Daemon.Huagai], [Dizhi.Xu])
        self.assertEqual(d.daemons[Daemon.Jiangxing], [Dizhi.Wu])
        self.assertEqual(d.daemons[Daemon.Tianxi], [Dizhi.Chou])
        self.assertEqual(d.daemons[Daemon.Tianyi], [Dizhi.Si])
        self.assertEqual(d.daemons[Daemon.Yangren], [Dizhi.Wu])
        self.assertEqual(d.daemons[Daemon.Zaisha], [Dizhi.Zi])
        self.assertEqual(d.daemons[Daemon.Mouxing], [Dizhi.Chen])

        # 卦身
        self.assertEqual(d.guashen, Dizhi.Shen)
        self.assertEqual(d.xianggui, [Dizhi.Yin, Dizhi.Mou])
        self.assertEqual(d.chuangzhang, [Dizhi.Zi, Dizhi.Hai])

    def test_standard_format(self):
        ds_dict = to_standard_format(
            DivinatorySymbol.create([1, 3, 0, 1, 0, 0], datetime.datetime(2024, 6, 11, 14, 5, 0))
        ).model_dump()

        import os

        schema_path = os.path.join(os.path.dirname(__file__), "../src/divicast/sixline/schema.json")
        with open(os.path.abspath(schema_path), "r") as f:
            my_schema = json.load(f)
        validate(instance=ds_dict, schema=my_schema)
        validate(instance=ds_dict, schema=StandardDivinatorySymbolOutput.model_json_schema())
