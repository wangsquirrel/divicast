import unittest

from divicast.birth_chart.birth import ZhuInfo
from divicast.entities.wuxing import Wuxing
from tests.helpers import build_chart


class TestBirthChartAnalysis(unittest.TestCase):
    def test_day_master_strength_strong(self):
        chart = build_chart("甲寅", "甲寅", "甲寅", "乙卯")

        self.assertIn(chart.chart_analysis.strength.day_master_strength.chinese_name, ["强", "极强"])
        self.assertGreaterEqual(chart.chart_analysis.strength.day_master_root_count, 3)
        self.assertGreater(chart.chart_analysis.strength.support_score, chart.chart_analysis.strength.opposition_score)
        self.assertIn(Wuxing.Wood, chart.chart_analysis.favorability.unfavorable_elements)

    def test_day_master_strength_weak(self):
        chart = build_chart("庚申", "己亥", "丙子", "戊子")

        self.assertIn(chart.chart_analysis.strength.day_master_strength.chinese_name, ["弱", "极弱"])
        self.assertEqual(chart.chart_analysis.strength.day_master_root_count, 0)
        self.assertLess(chart.chart_analysis.strength.support_ratio, 0.35)
        self.assertIn(Wuxing.Wood, chart.chart_analysis.favorability.favorable_elements)


if __name__ == "__main__":
    unittest.main()
