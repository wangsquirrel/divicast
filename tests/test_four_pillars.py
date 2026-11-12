import pickle
import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from tyme4py.eightchar.provider.impl import DefaultEightCharProvider
from tyme4py.lunar import LunarHour
from tyme4py.solar import SolarTime

from divicast.birth_chart.birth import BirthChart
from divicast.entities.ganzhi import SixtyJiazi, Tiangan
from divicast.entities.misc import Gender
from divicast.entities.pillars import FourPillars
from divicast.sixline import DivinatorySymbol
from divicast.time_utils import create_four_pillars, four_pillars_from_tyme


def sample_pillars() -> FourPillars:
    return FourPillars(
        year=SixtyJiazi.parse("甲辰"),
        month=SixtyJiazi.parse("庚午"),
        day=SixtyJiazi.parse("丙午"),
        hour=SixtyJiazi.parse("乙未"),
    )


class TestFourPillars(unittest.TestCase):
    def test_equality_and_hashing_include_pillar_positions(self) -> None:
        original = sample_pillars()
        equal = sample_pillars()
        swapped = replace(original, year=original.month, month=original.year)
        self.assertIsNot(original, equal)
        self.assertEqual(original, equal)
        self.assertEqual(hash(original), hash(equal))
        self.assertNotEqual(original, swapped)
        self.assertNotEqual(original, tuple(original))
        self.assertEqual(2, len({original, equal, swapped}))
        self.assertEqual("saved", {original: "saved"}[equal])

    def test_every_position_requires_a_validated_ganzhi(self) -> None:
        pillars = sample_pillars()
        lookalike = SimpleNamespace(gan=pillars.day.gan, zhi=pillars.day.zhi)
        for position in ("year", "month", "day", "hour"):
            for invalid in (None, "甲子", True, (pillars.day.gan, pillars.day.zhi), lookalike):
                with self.subTest(position=position, value=invalid), self.assertRaisesRegex(TypeError, position):
                    replace(pillars, **{position: invalid})

    def test_pillars_and_nested_values_are_immutable(self) -> None:
        pillars = sample_pillars()
        lookup = {pillars: "saved"}
        for position in ("year", "month", "day", "hour"):
            with self.subTest(position=position):
                with self.assertRaises(FrozenInstanceError):
                    setattr(pillars, position, SixtyJiazi.parse("甲子"))
                with self.assertRaises(FrozenInstanceError):
                    delattr(pillars, position)
        with self.assertRaises(FrozenInstanceError):
            pillars.day.gan = Tiangan.Jia
        self.assertEqual("saved", lookup[sample_pillars()])

    def test_iteration_and_text_use_year_month_day_hour_order(self) -> None:
        pillars = sample_pillars()
        self.assertEqual("甲辰 庚午 丙午 乙未", str(pillars))
        self.assertEqual((pillars.year, pillars.month, pillars.day, pillars.hour), tuple(pillars))
        self.assertEqual(pillars, pickle.loads(pickle.dumps(pillars)))


class TestSharedPillars(unittest.TestCase):
    def test_tyme_adapter_converts_existing_values_without_calendar_recalculation(self) -> None:
        lunar_hour = SolarTime.from_ymd_hms(2026, 9, 16, 23, 0, 0).get_lunar_hour()
        eight_char = DefaultEightCharProvider().get_eight_char(lunar_hour)
        with (
            patch.object(LunarHour, "provider", None),
            patch.object(DefaultEightCharProvider, "get_eight_char", side_effect=AssertionError("do not recalculate")),
        ):
            pillars = four_pillars_from_tyme(eight_char)
        self.assertIs(type(pillars), FourPillars)
        self.assertEqual("甲午", str(pillars.day))
        for pillar in pillars:
            self.assertIs(type(pillar), SixtyJiazi)

    def test_both_charts_share_domain_types_and_preserve_different_defaults(self) -> None:
        dt = datetime(2026, 9, 16, 23)
        birth_chart = BirthChart.create(dt, Gender.Male)
        sixline = DivinatorySymbol.create(now=dt, line_values=[7] * 6)
        self.assertIs(type(birth_chart.pillars), FourPillars)
        self.assertIs(type(sixline.bazi), FourPillars)
        self.assertEqual("癸巳", str(birth_chart.pillars.day))
        self.assertEqual("甲午", str(sixline.bazi.day))
        self.assertEqual(create_four_pillars(dt), sixline.bazi)
        for pillar, info in zip(
            birth_chart.pillars,
            (birth_chart.yearzhu, birth_chart.monthzhu, birth_chart.dayzhu, birth_chart.bihourzhu),
            strict=True,
        ):
            self.assertIs(info.sixty_jiazi, pillar)
        with self.assertRaises(AttributeError):
            birth_chart.pillars = sample_pillars()

    def test_both_charts_agree_when_given_the_same_calendar_rule(self) -> None:
        for dt in (
            datetime(2026, 9, 16, 22, 59, 59),
            datetime(2026, 9, 16, 23),
            datetime(2026, 9, 17),
            datetime(2020, 2, 4, 17, 3, 11),
            datetime(2020, 2, 4, 17, 3, 12),
        ):
            for rule in ("default_next_day", "lunar_sect2_day_same"):
                with self.subTest(time=dt, rule=rule):
                    rules = {"zi_hour": rule}
                    birth_chart = BirthChart.create(dt, Gender.Male, calc_rules=rules)
                    sixline = DivinatorySymbol.create(now=dt, line_values=[7] * 6, calc_rules=rules)
                    self.assertEqual(birth_chart.pillars, sixline.bazi)

    def test_explicit_pillars_are_shared_without_copying_or_recalculation(self) -> None:
        pillars = sample_pillars()
        with patch(
            "divicast.sixline.divinatory_symbol.create_four_pillars",
            side_effect=AssertionError("do not recalculate"),
        ):
            # 姤需要装伏神，连同辅助卦一起验证显式四柱的复用。
            chart = DivinatorySymbol.create(cnts=[2, 1, 1, 1, 1, 1], now=datetime(2024, 1, 1), bazi=pillars)
        self.assertIs(chart.bazi, pillars)
        self.assertEqual("provided", chart.calendar.pillar_source)
        self.assertIsNone(chart.calendar.zi_hour)

    def test_sixline_rejects_unvalidated_pillar_containers(self) -> None:
        pillars = sample_pillars()
        lookalike = SimpleNamespace(year=pillars.year, month=pillars.month, day=pillars.day, hour=pillars.hour)
        for invalid in (str(pillars), tuple(pillars), lookalike):
            with self.subTest(value=invalid), self.assertRaises(TypeError):
                DivinatorySymbol.create(now=datetime(2024, 1, 1), line_values=[7] * 6, bazi=invalid)
