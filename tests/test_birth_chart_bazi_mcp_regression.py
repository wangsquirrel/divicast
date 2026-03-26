import json
import unittest
from datetime import datetime
from pathlib import Path

from divicast.birth_chart.birth import BirthChart
from divicast.birth_chart.output import to_standard_format
from divicast.entities.misc import Gender


FIXTURE_PATH = Path(__file__).with_name("fixtures") / "bazi_mcp_goldens.json"
EXPECTED_CATEGORIES = {
    "lichun_boundary",
    "solar_term_boundary",
    "zi_hour",
    "leap_month",
    "fortune_direction",
}


def _parse_start_date(value: str) -> str:
    if "年" not in value:
        return value
    year_part, rest = value.split("年", 1)
    month_part, rest = rest.split("月", 1)
    day_part = rest.split("日", 1)[0]
    return f"{int(year_part)}-{int(month_part)}-{int(day_part)}"


def _normalize_actual_output(dt: datetime, gender_value: int) -> dict:
    gender = Gender.Male if gender_value == 1 else Gender.Female
    output = to_standard_format(BirthChart.create(dt, gender), dt).model_dump(mode="json", exclude_none=True)
    four = output["natal_chart"]["four_pillars"]
    return {
        "personal_info": {
            "gregorian_birth": output["personal_info"]["gregorian_birth"],
            "lunar_birth": output["personal_info"]["lunar_birth"],
            "gender": output["personal_info"]["gender"],
            "zodiac": output["personal_info"]["zodiac"],
        },
        "natal_chart": {
            "day_master": output["natal_chart"]["day_master"],
            "day_master_element": output["natal_chart"]["day_master_element"],
            "day_master_yinyang": output["natal_chart"]["day_master_yinyang"],
            "conception_pillar": output["natal_chart"]["conception_pillar"],
            "fetal_breath": output["natal_chart"]["fetal_breath"],
            "body_pillar": output["natal_chart"]["body_pillar"],
            "life_pillar": output["natal_chart"]["life_pillar"],
            "four_pillars": {
                key: four[key]
                for key in ("year", "month", "day", "hour")
            },
        },
        "luck_cycles": {
            "start_age": output["luck_cycles"]["start_age"],
            "start_date": _parse_start_date(output["luck_cycles"]["start_date"]),
            "direction": output["luck_cycles"]["direction"],
            "major_cycles": [
                {
                    "age_range": cycle["age_range"],
                    "pillar": cycle["pillar"],
                    "year_range": cycle["year_range"],
                    "tengod": cycle["tengod"],
                }
                for cycle in output["luck_cycles"]["major_cycles"]
            ],
        },
    }


def _assert_nested_equal(testcase: unittest.TestCase, expected, actual, path: str):
    if path.endswith("shensha"):
        testcase.assertEqual(set(expected), set(actual), path)
        return
    if isinstance(expected, dict):
        testcase.assertIsInstance(actual, dict, path)
        testcase.assertEqual(set(expected.keys()), set(actual.keys()), path)
        for key in expected:
            _assert_nested_equal(testcase, expected[key], actual[key], f"{path}.{key}" if path else key)
        return
    if isinstance(expected, list):
        testcase.assertIsInstance(actual, list, path)
        testcase.assertEqual(len(expected), len(actual), path)
        for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
            _assert_nested_equal(testcase, expected_item, actual_item, f"{path}[{index}]")
        return
    testcase.assertEqual(expected, actual, path)


class TestBirthChartBaziMcpRegression(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.fixture = fixture
        cls.samples = fixture["samples"]

    def test_fixture_contract(self):
        self.assertTrue(FIXTURE_PATH.exists())
        self.assertEqual("cantian-ai/bazi-mcp", self.fixture["source"]["repo"])
        self.assertEqual("dev", self.fixture["source"]["branch"])
        self.assertEqual(2, self.fixture["source"]["eight_char_provider_sect"])
        self.assertEqual("buildBazi", self.fixture["source"]["seconds_preserved_via"])
        self.assertEqual(self.fixture["sample_count"], len(self.samples))
        self.assertGreaterEqual(len(self.samples), 50)
        self.assertLessEqual(len(self.samples), 100)
        self.assertEqual(EXPECTED_CATEGORIES, {sample["category"] for sample in self.samples})

    def test_standard_output_matches_bazi_mcp_golden_set(self):
        for sample in self.samples:
            with self.subTest(sample=sample["id"], category=sample["category"]):
                dt = datetime.fromisoformat(sample["solar_datetime"])
                actual = _normalize_actual_output(dt, sample["gender"])
                _assert_nested_equal(self, sample["expected"], actual, sample["id"])


if __name__ == "__main__":
    unittest.main()
