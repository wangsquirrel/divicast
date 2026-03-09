import datetime
import unittest

from divicast.birth_chart.birth import BirthChart, Gender
from divicast.birth_chart.output import (StandardBirthChartOutput,
                                         to_standard_format)


class TestBirthChart(unittest.TestCase):
    def test_output(self):
        output = to_standard_format(
            BirthChart.create(datetime.datetime(2025, 10, 10, 15, 39), Gender.MAN),
            datetime.datetime(2026, 3, 21, 12, 30),
        )
        print(output.model_dump_json(indent=2))
        print(StandardBirthChartOutput.model_json_schema())
        self.assertEqual(12, len(output.target_flow.flow_months))
        self.assertEqual("立春", output.target_flow.flow_months[0].solar_term)
        self.assertTrue(output.target_flow.minor_pillar)
        self.assertEqual(
            "solar_term_month_start",
            output.natal_chart.calc_rules.get("flow_months"),
        )
        self.assertEqual(
            "child_limit",
            output.natal_chart.calc_rules.get("minor_fortune"),
        )
        self.assertEqual(
            "lichun_boundary",
            output.natal_chart.calc_rules.get("flow_year"),
        )
