import datetime
import unittest

from divicast.birth_chart.birth import BirthChart, Gender, ZhuInfo
from divicast.birth_chart.geju import Geju
from tests.helpers import build_chart


class TestGeju(unittest.TestCase):
    def test_kuigang_real_birth_charts(self):
        cases = [
            (datetime.datetime(2024, 5, 28, 12, 0, 0), "壬辰"),
            (datetime.datetime(2024, 1, 17, 12, 0, 0), "庚辰"),
            (datetime.datetime(2024, 2, 16, 12, 0, 0), "庚戌"),
            (datetime.datetime(2024, 2, 4, 12, 0, 0), "戊戌"),
        ]

        for dt, pillar in cases:
            with self.subTest(pillar=pillar):
                chart = BirthChart.create(dt, Gender.Male)
                self.assertEqual(chart.dayzhu.gan.chinese_name + chart.dayzhu.zhi.chinese_name, pillar)
                self.assertEqual(chart.chart_analysis.geju.geju, Geju.KUIGANG)

    def test_hard_special_geju_cases(self):
        cases = [
            ("归禄格", ("甲寅", "甲寅", "甲卯", "乙卯"), Geju.GUI_LU),
            ("壬骑龙背格", ("甲辰", "庚辰", "壬辰", "壬辰"), Geju.QI_QIANG_BEI),
            ("井栏叉格", ("甲子", "丙寅", "庚子", "丁卯"), Geju.JING_LAN_CHA),
            ("六甲趋干格", ("庚申", "丙子", "甲午", "乙亥"), Geju.LIU_JIA_QU_GAN),
            ("六乙鼠贵格", ("庚申", "丙子", "乙卯", "丙子"), Geju.LIU_YI_SHU_GUI),
            ("六阴朝阳格", ("庚申", "丙子", "辛巳", "丁丑"), Geju.LIU_YIN_CHAO_YANG),
            ("六壬趋艮格", ("庚申", "丙子", "壬寅", "丁卯"), Geju.LIU_REN_QU_GEN),
            ("勾陈得位格", ("庚申", "丙子", "戊丑", "丁卯"), Geju.GOU_CHEN_DE_WEI),
            ("玄武当权格", ("庚申", "壬子", "壬午", "辛亥"), Geju.XUAN_WU_DANG_QUAN),
        ]

        for label, pillars, expected in cases:
            with self.subTest(geju=label):
                chart = build_chart(*pillars)
                self.assertEqual(chart.chart_analysis.geju.geju, expected)

    def test_zhengge_cases(self):
        cases = [
            ("正官格", ("癸亥", "辛未", "壬申", "己卯"), Geju.ZHENG_GUAN),
            ("七杀格", ("乙巳", "丙戌", "壬子", "戊申"), Geju.QI_SHA),
            ("正财格", ("己巳", "戊戌", "乙卯", "庚申"), Geju.ZHENG_CAI),
            ("偏财格", ("己巳", "甲午", "乙丑", "戊寅"), Geju.PIAN_CAI),
            ("正印格", ("乙亥", "乙卯", "丙申", "甲午"), Geju.ZHENG_YIN),
            ("偏印格", ("辛未", "丙申", "甲子", "壬寅"), Geju.PIAN_YIN),
            ("食神格", ("戊申", "甲辰", "丙寅", "壬寅"), Geju.SHI_SHEN),
            ("伤官格", ("甲子", "丁巳", "丁酉", "戊辰"), Geju.SHANG_GUAN),
            ("比肩格", ("壬辰", "己未", "己亥", "戊午"), Geju.BI_JIAN),
            ("劫财格", ("甲午", "己亥", "乙巳", "戊午"), Geju.JIE_CAI),
        ]

        for label, pillars, expected in cases:
            with self.subTest(geju=label):
                chart = build_chart(*pillars)
                self.assertEqual(chart.chart_analysis.geju.geju, expected)

    def test_soft_special_and_regular_cases(self):
        cases = [
            ("两神成象格", ("庚申", "癸酉", "癸亥", "丙寅"), Geju.LIANG_SHEN_CHENG_XIANG),
            ("半壁江山格", ("辛丑", "丙辰", "庚寅", "辛丑"), Geju.BAN_BI_JIANG_SHAN),
            ("普通格局", ("壬申", "庚子", "戊午", "乙卯"), Geju.REGULAR),
        ]

        for label, pillars, expected in cases:
            with self.subTest(geju=label):
                chart = build_chart(*pillars)
                self.assertEqual(chart.chart_analysis.geju.geju, expected)

    def test_zhuanwang_and_cong_cases(self):
        cases = [
            ("曲直格", ("甲寅", "甲寅", "甲寅", "乙卯"), Geju.QU_ZHI),
            ("炎上格", ("甲寅", "甲午", "丙午", "甲寅"), Geju.YAN_SHANG),
            ("稼穑格", ("戊午", "丙辰", "己未", "戊子"), Geju.JIA_SE),
            ("润下格", ("己亥", "丙子", "壬子", "癸亥"), Geju.RUN_XIA),
            ("从革格", ("壬子", "辛酉", "辛丑", "戊寅"), Geju.CONG_GE),
            ("从财格", ("己戌", "戊丑", "乙酉", "己戌"), Geju.CONG_CAI),
            ("从杀格", ("壬子", "癸亥", "丙子", "壬申"), Geju.CONG_SHA),
            ("从儿格", ("丁卯", "乙未", "癸卯", "甲寅"), Geju.CONG_ER),
            ("从强格", ("辛酉", "庚申", "壬子", "辛亥"), Geju.CONG_QIANG),
        ]

        for label, pillars, expected in cases:
            with self.subTest(geju=label):
                chart = build_chart(*pillars)
                self.assertEqual(chart.chart_analysis.geju.geju, expected)

    def test_huaqi_cases(self):
        cases = [
            ("化甲格", ("戊申", "己丑", "甲申", "庚戌"), Geju.HUA_JIA),
            ("化乙格", ("戊申", "癸酉", "乙未", "庚戌"), Geju.HUA_YI),
            ("化丙格", ("乙亥", "甲子", "丙子", "辛亥"), Geju.HUA_BING),
        ]

        for label, pillars, expected in cases:
            with self.subTest(geju=label):
                chart = build_chart(*pillars)
                self.assertEqual(chart.chart_analysis.geju.geju, expected)

    def test_qiqiang_bei_takes_priority_over_kuigang(self):
        chart = build_chart("甲辰", "庚辰", "壬辰", "壬辰")
        self.assertEqual(chart.chart_analysis.geju.geju, Geju.QI_QIANG_BEI)

    def test_soft_special_is_checked_before_regular_fallback(self):
        chart = build_chart("庚申", "癸酉", "癸亥", "丙寅")
        self.assertEqual(chart.chart_analysis.geju.geju, Geju.LIANG_SHEN_CHENG_XIANG)

    def test_regular_real_birth_chart_is_not_forced_to_kuigang(self):
        chart = BirthChart.create(datetime.datetime(2024, 1, 1, 12, 0, 0), Gender.Male)
        self.assertNotEqual(chart.chart_analysis.geju.geju, Geju.KUIGANG)


if __name__ == "__main__":
    unittest.main()
