import unittest
from datetime import datetime

from divicast.birth_chart.birth import BirthChart, ZhuInfo
from divicast.birth_chart.output import to_standard_format
from divicast.entities.daemon import Daemon
from divicast.entities.ganzhi import CangganType, Dizhi, Nayin, Shishen, SixtyJiazi, Tiangan, TwelveZhangsheng
from divicast.entities.misc import Gender


class TestZhuInfoConstruction(unittest.TestCase):
    def test_all_pillar_information_is_available_immediately(self) -> None:
        value = SixtyJiazi.parse("甲子")
        zhu = ZhuInfo(value, day_master=Tiangan.Bing, shensha=(Daemon.Tianyiguiren,))

        self.assertIs(value, zhu.sixty_jiazi)
        self.assertIs(Tiangan.Jia, zhu.gan)
        self.assertIs(Dizhi.Zi, zhu.zhi)
        self.assertIs(Shishen.PianYin, zhu.zhuxing)
        self.assertEqual([(Tiangan.Gui, CangganType.MAIN)], [(item.gan, item.canggan_type) for item in zhu.canggan])
        self.assertEqual([Shishen.ZhengGuan], zhu.fuxing)
        self.assertIs(TwelveZhangsheng.Tai, zhu.xingyun)
        self.assertIs(TwelveZhangsheng.MuYu, zhu.zizuo)
        self.assertIs(Nayin.HaiZhongJin, zhu.nayin)
        self.assertEqual((Dizhi.Xu, Dizhi.Hai), zhu.kongwang)
        self.assertEqual([Daemon.Tianyiguiren], zhu.shensha)

    def test_contextual_values_use_the_supplied_day_master(self) -> None:
        value = SixtyJiazi.parse("甲子")
        jia_chart = ZhuInfo(value, day_master=Tiangan.Jia, shensha=())
        bing_chart = ZhuInfo(value, day_master=Tiangan.Bing, shensha=())

        self.assertIs(Shishen.BiJian, jia_chart.zhuxing)
        self.assertEqual([Shishen.ZhengYin], jia_chart.fuxing)
        self.assertIs(TwelveZhangsheng.MuYu, jia_chart.xingyun)
        self.assertIs(Shishen.PianYin, bing_chart.zhuxing)
        self.assertEqual([Shishen.ZhengGuan], bing_chart.fuxing)
        self.assertIs(TwelveZhangsheng.Tai, bing_chart.xingyun)
        self.assertEqual(jia_chart.zizuo, bing_chart.zizuo)
        self.assertEqual([], jia_chart.shensha)

    def test_context_is_required_even_when_shensha_is_empty(self) -> None:
        value = SixtyJiazi.parse("甲子")
        for context in ({}, {"day_master": Tiangan.Jia}, {"shensha": ()}):
            with self.subTest(context=context), self.assertRaises(TypeError):
                ZhuInfo(value, **context)

    def test_invalid_context_is_rejected_during_construction(self) -> None:
        value = SixtyJiazi.parse("甲子")
        for day_master in (None, "甲", 0, False, Dizhi.Zi):
            with self.subTest(day_master=day_master), self.assertRaises(TypeError):
                ZhuInfo(value, day_master=day_master, shensha=())
        for shensha in (None, "", b"", bytearray(), {Daemon.Wenchang}, ["文昌"], [Daemon.Wenchang, None]):
            with self.subTest(shensha=shensha), self.assertRaises(TypeError):
                ZhuInfo(value, day_master=Tiangan.Jia, shensha=shensha)

    def test_shensha_order_is_preserved_without_sharing_the_callers_list(self) -> None:
        source = [Daemon.Wenchang, Daemon.Tianyiguiren]
        value = SixtyJiazi.parse("甲子")
        first = ZhuInfo(value, day_master=Tiangan.Jia, shensha=source)
        second = ZhuInfo(value, day_master=Tiangan.Jia, shensha=source)

        source.clear()
        self.assertEqual([Daemon.Wenchang, Daemon.Tianyiguiren], first.shensha)
        first.shensha.append(Daemon.Lushen)
        self.assertEqual([Daemon.Wenchang, Daemon.Tianyiguiren], second.shensha)


class TestBirthChartConstruction(unittest.TestCase):
    def test_direct_construction_is_ready_for_output_and_equivalent_to_create(self) -> None:
        dt = datetime(2024, 1, 15, 23)
        target = datetime(2026, 3, 21, 12, 30)
        for rules in (
            None,
            {"zi_hour": "default_next_day"},
            {"zi_hour": "lunar_sect2_day_same"},
            {"minggong": "month_hour_simple"},
        ):
            for gender in Gender:
                with self.subTest(rules=rules, gender=gender):
                    direct = BirthChart(dt, gender, calc_rules=rules)
                    factory = BirthChart.create(dt, gender, calc_rules=rules)
                    self.assertIsNotNone(direct.chart_analysis.strength.day_master_strength)
                    self.assertIsNotNone(direct.chart_analysis.geju.geju)
                    self.assertEqual(
                        to_standard_format(factory, target).model_dump(mode="json"),
                        to_standard_format(direct, target).model_dump(mode="json"),
                    )

    def test_both_entry_points_reject_invalid_gender(self) -> None:
        dt = datetime(2024, 1, 15, 23)
        for entry in (BirthChart, BirthChart.create):
            for gender in (None, "男", 1, False, Tiangan.Yi):
                with self.subTest(entry=entry, gender=gender), self.assertRaises(TypeError):
                    entry(dt, gender)
