import datetime
import unittest

from divicast.birth_chart.birth import BirthChart, Gender
from divicast.birth_chart.output import ChartAnalysisOutput, StandardBirthChartOutput, to_standard_format


class TestBirthChart(unittest.TestCase):
    def test_output(self):
        output = to_standard_format(
            BirthChart.create(datetime.datetime(2025, 10, 10, 15, 39), Gender.Male),
            datetime.datetime(2026, 3, 21, 12, 30),
        )
        self.assertEqual(12, len(output.target_flow.flow_months))
        self.assertEqual("立春", output.target_flow.flow_months[0].solar_term)
        self.assertTrue(output.target_flow.minor_pillar)
        self.assertEqual(
            "solar_term_month_start",
            output.natal_chart.calc_rules.get("flow_months"),
        )
        self.assertEqual(
            "heuristic_scoring_v1",
            output.natal_chart.calc_rules.get("analysis_framework"),
        )
        self.assertEqual(
            "lunar_sect2_day_same",
            output.natal_chart.calc_rules.get("zi_hour"),
        )
        self.assertEqual(
            "strength_balance_heuristic",
            output.natal_chart.calc_rules.get("favorability"),
        )
        self.assertEqual(
            "rule_based_candidate_match",
            output.natal_chart.calc_rules.get("geju"),
        )
        self.assertEqual(
            "core_relations_v2",
            output.natal_chart.calc_rules.get("relations"),
        )
        self.assertEqual(
            "child_limit",
            output.natal_chart.calc_rules.get("minor_fortune"),
        )
        self.assertEqual(
            "lichun_boundary",
            output.natal_chart.calc_rules.get("flow_year"),
        )
        self.assertIsInstance(output.heuristic_analysis, ChartAnalysisOutput)
        self.assertEqual("土", output.heuristic_analysis.wuxing.month_zhi_wuxing)
        self.assertIn("比劫", output.heuristic_analysis.ten_god.ten_god_family_scores)
        self.assertIsInstance(output.heuristic_analysis.relations.events, list)
        self.assertTrue(output.heuristic_analysis.relations.by_pillar.model_dump())

    def test_zi_hour_rule_can_switch_back_to_next_day(self):
        default_chart = BirthChart.create(datetime.datetime(2024, 1, 15, 23, 0), Gender.Male)
        next_day_chart = BirthChart.create(
            datetime.datetime(2024, 1, 15, 23, 0),
            Gender.Male,
            calc_rules={"zi_hour": "default_next_day"},
        )

        self.assertEqual("戊", str(default_chart.dayzhu.gan))
        self.assertEqual("己", str(next_day_chart.dayzhu.gan))
