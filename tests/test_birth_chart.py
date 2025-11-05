import datetime
import unittest

from divicast.birth_chart.birth import BirthChart, Gender
from divicast.birth_chart.output import (StandardBirthChartOutput,
                                         to_standard_format)


class TestBirthChart(unittest.TestCase):
    def test_output(self):
        print(to_standard_format(BirthChart.create(
            datetime.datetime(2025, 10, 10, 15, 39), Gender.MAN)).model_dump_json(indent=2))
        print(StandardBirthChartOutput.model_json_schema())
