from __future__ import annotations

import io
import json
import unittest
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from itertools import product
from pathlib import Path
from unittest.mock import patch

from jsonschema import validate
from pydantic import ValidationError
from tyme4py.lunar import LunarHour

from divicast.sixline import DivinatorySymbol, plain_draw_divination, rich_draw_divination, to_standard_format
from divicast.sixline.divinatory_symbol import create_bazi, create_line_position
from divicast.sixline.output import StandardDivinatorySymbolOutput, cnt_to_str
from divicast.time_utils import create_four_pillars


REFERENCE = json.loads((Path(__file__).parent / "fixtures/sixline_reference.json").read_text(encoding="utf-8"))
BY_NAME = {case["name"]: case for case in REFERENCE["hexagrams"]}
BY_BITS = {case["bits"]: case for case in REFERENCE["hexagrams"]}
DEFAULT_TIME = datetime(2024, 1, 1, 12)


def chart(now=DEFAULT_TIME, **kwargs):
    return to_standard_format(DivinatorySymbol.create(now=now, **kwargs)).model_dump(mode="json", exclude_none=True)


def old_fields(result):
    return {key: value for key, value in result.items() if key not in ("line_values", "casting", "calendar")}


class TestSixlineContract(unittest.TestCase):
    def test_64_hexagrams_against_classical_palace_table(self):
        self.assertEqual(len(BY_BITS), 64)
        for case in REFERENCE["hexagrams"]:
            with self.subTest(name=case["name"]):
                result = chart(line_values=[7 if bit == "1" else 8 for bit in case["bits"]])
                self.assertEqual(result["benguaming"], case["name"])
                self.assertEqual(result["bianguaming"], case["name"])
                self.assertEqual(result["guagong"], case["palace"])
                self.assertEqual([i for i in range(1, 7) if result[f"yao_{i}"]["origin"]["is_subject"]], [case["shi"]])
                self.assertEqual([i for i in range(1, 7) if result[f"yao_{i}"]["origin"]["is_object"]], [case["ying"]])

    def test_pure_hexagram_najia_and_relatives(self):
        for name, expected in REFERENCE["pure_najia"].items():
            with self.subTest(name=name):
                result = chart(line_values=[7 if bit == "1" else 8 for bit in BY_NAME[name]["bits"]])
                origins = [result[f"yao_{i}"]["origin"] for i in range(1, 7)]
                for field in ("gan", "zhi", "wuxing"):
                    self.assertEqual("".join(yao[field] for yao in origins), expected[field])
                self.assertEqual([yao["relative"] for yao in origins], expected["relatives"])
                self.assertTrue(all("fushen" not in yao for yao in origins))

    def test_fushen_at_original_palace_positions(self):
        cases = {
            "姤": {2: {"relative": "妻财", "gan": "甲", "zhi": "寅", "wuxing": "木"}},
            "遁": {
                1: {"relative": "子孙", "gan": "甲", "zhi": "子", "wuxing": "水"},
                2: {"relative": "妻财", "gan": "甲", "zhi": "寅", "wuxing": "木"},
            },
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                result = chart(line_values=[7 if bit == "1" else 8 for bit in BY_NAME[name]["bits"]])
                actual = {
                    i: result[f"yao_{i}"]["origin"]["fushen"]
                    for i in range(1, 7)
                    if "fushen" in result[f"yao_{i}"]["origin"]
                }
                self.assertEqual(actual, expected)

    def test_coin_sides_match_standard_values_and_legacy(self):
        for text_count, value, name, variant in [
            (0, 9, "乾", "坤"),
            (1, 8, "坤", "坤"),
            (2, 7, "乾", "乾"),
            (3, 6, "坤", "乾"),
        ]:
            with self.subTest(text_count=text_count):
                text = chart(coin_counts=[text_count] * 6, coin_side="text")
                back = chart(coin_counts=[3 - text_count] * 6, coin_side="back")
                standard = chart(line_values=[value] * 6)
                legacy = chart(cnts=[value - 6] * 6)
                self.assertEqual(old_fields(text), old_fields(back))
                self.assertEqual(old_fields(text), old_fields(standard))
                self.assertEqual(old_fields(text), old_fields(legacy))
                self.assertEqual((text["benguaming"], text["bianguaming"]), (name, variant))
                self.assertEqual(text["line_values"], [value] * 6)
                self.assertEqual(
                    text["casting"], {"input_format": "coin_counts", "values": [text_count] * 6, "coin_side": "text"}
                )

    def test_legacy_mixed_chart_and_variant_original_palace(self):
        legacy = chart(cnts=[0, 1, 2, 3, 0, 1])
        self.assertEqual(old_fields(legacy), old_fields(chart(line_values=[6, 7, 8, 9, 6, 7])))
        self.assertEqual((legacy["benguaming"], legacy["bianguaming"], legacy["guagong"]), ("未济", "中孚", "离"))
        self.assertEqual(legacy["yaogua"], [0, 1, 2, 3, 0, 1])
        self.assertEqual(legacy["casting"], {"input_format": "legacy_yaogua", "values": [0, 1, 2, 3, 0, 1]})
        self.assertEqual(
            legacy["yao_3"]["origin"]["fushen"], {"relative": "官鬼", "gan": "己", "zhi": "亥", "wuxing": "水"}
        )
        self.assertEqual(
            legacy["yao_1"]["variant"], {"relative": "兄弟", "gan": "丁", "zhi": "巳", "wuxing": "火", "line": "⚊"}
        )
        self.assertFalse(legacy["yao_2"]["origin"]["is_changed"])
        self.assertEqual(legacy["yao_2"]["origin"]["zhi"], "辰")
        self.assertEqual(legacy["yao_2"]["variant"]["zhi"], "卯")

    def test_all_4096_casts_have_correct_named_origin_variant_and_motion(self):
        truth = {6: ("0", "1", True), 7: ("1", "1", False), 8: ("0", "0", False), 9: ("1", "0", True)}
        for values in product((6, 7, 8, 9), repeat=6):
            with self.subTest(values=values):
                result = chart(line_values=values)
                self.assertEqual(result["benguaming"], BY_BITS["".join(truth[v][0] for v in values)]["name"])
                self.assertEqual(result["bianguaming"], BY_BITS["".join(truth[v][1] for v in values)]["name"])
                for i, value in enumerate(values, 1):
                    yao = result[f"yao_{i}"]
                    origin, variant, moving = truth[value]
                    self.assertEqual(yao["origin"]["line"], "⚊" if origin == "1" else "⚋")
                    self.assertEqual(yao["variant"]["line"], "⚊" if variant == "1" else "⚋")
                    self.assertIs(yao["origin"]["is_changed"], moving)

    def test_random_three_coin_weights_and_replay(self):
        observed = Counter()
        with patch("divicast.sixline.casting.random.randrange", side_effect=list(range(8)) * 6) as random_draw:
            for _ in range(8):
                result = chart()
                self.assertEqual(result["casting"], {"input_format": "random_three_coins"})
                observed.update(result["line_values"])
                self.assertEqual(old_fields(chart(line_values=result["line_values"])), old_fields(result))
            self.assertEqual(random_draw.call_count, 48)
        self.assertEqual(observed, {6: 6, 7: 18, 8: 18, 9: 6})

    def test_invalid_inputs_fail_before_randomization(self):
        cases = [
            {"cnts": []},
            {"cnts": [1] * 5},
            {"cnts": [1] * 7},
            {"cnts": [4] * 6},
            {"cnts": [True] * 6},
            {"cnts": [1.0] * 6},
            {"cnts": "111111"},
            {"cnts": 1},
            {"line_values": [6] * 5},
            {"line_values": [10] * 6},
            {"line_values": [7.0] * 6},
            {"coin_counts": [True] * 6, "coin_side": "text"},
            {"coin_counts": [4] * 6, "coin_side": "text"},
            {"coin_counts": [0] * 6},
            {"coin_counts": [0] * 6, "coin_side": "heads"},
            {"coin_side": "text"},
            {"line_values": [7] * 6, "cnts": [1] * 6},
            {"line_values": [7] * 6, "coin_counts": [2] * 6, "coin_side": "text"},
        ]
        with patch("divicast.sixline.casting.random.randrange") as random_draw:
            for kwargs in cases:
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    chart(**kwargs)
            random_draw.assert_not_called()
        for value in (-1, 4, True, 1.0, "1", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                create_line_position(value)

    def test_input_records_are_snapshots(self):
        for keyword, values, extra in [
            ("cnts", [1] * 6, {}),
            ("line_values", [7] * 6, {}),
            ("coin_counts", [2] * 6, {"coin_side": "text"}),
        ]:
            with self.subTest(keyword=keyword):
                ds = DivinatorySymbol.create(now=DEFAULT_TIME, **{keyword: values}, **extra)
                before = to_standard_format(ds).model_dump(mode="json")
                values[0] = 0
                self.assertEqual(to_standard_format(ds).model_dump(mode="json"), before)
                self.assertIsInstance(ds.casting.values, tuple)
                with self.assertRaises(ValidationError):
                    ds.casting.values = (0,) * 6

    def test_rendering_preserves_input_meaning(self):
        legacy = DivinatorySymbol.create([0] * 6, DEFAULT_TIME)
        plain = plain_draw_divination(legacy)
        self.assertIn("旧版编码", plain)
        self.assertIn("老阴", plain)
        self.assertNotIn("(背)", plain)
        self.assertNotIn("(字)", plain)
        self.assertIn("老阴", cnt_to_str(0))
        for side, label in (("text", "字面"), ("back", "背面")):
            ds = DivinatorySymbol.create(now=DEFAULT_TIME, coin_counts=[3] * 6, coin_side=side)
            plain = plain_draw_divination(ds)
            self.assertIn(label + "枚数: 3 3 3 3 3 3", plain)
            self.assertIn("6(老阴)" if side == "text" else "9(老阳)", plain)
            stream = io.StringIO()
            with redirect_stdout(stream):
                rich_draw_divination(ds)
            self.assertIn(label + "枚数", stream.getvalue())

    def test_lichun_minute_and_second_boundaries(self):
        for minute, second, year, month in [
            (0, 0, "乙巳", "己丑"),
            (1, 50, "乙巳", "己丑"),
            (1, 52, "丙午", "庚寅"),
            (30, 0, "丙午", "庚寅"),
        ]:
            with self.subTest(minute=minute, second=second):
                result = chart(datetime(2026, 2, 4, 4, minute, second), line_values=[7] * 6)
                self.assertEqual(result["bazi"].split()[:2], [year, month])
                self.assertEqual(result["yuejian"], month[1])
                self.assertEqual(result["time"], f"2026-02-04 04:{minute:02}:{second:02}")

    def test_late_zi_day_void_and_spirits(self):
        for day, hour, minute, second, pillar, empty, spirit in [
            (16, 22, 59, 59, "癸巳", "午未", "玄武"),
            (16, 23, 0, 0, "甲午", "辰巳", "青龙"),
            (17, 0, 0, 0, "甲午", "辰巳", "青龙"),
        ]:
            with self.subTest(day=day, hour=hour):
                dt = datetime(2026, 9, day, hour, minute, second)
                result = chart(dt, line_values=[7] * 6)
                self.assertEqual(result["bazi"].split()[2], pillar)
                self.assertEqual(result["kongwang"], empty)
                self.assertEqual(result["yao_1"]["liushen"], spirit)
                self.assertEqual(result["time"], dt.isoformat(sep=" "))
                self.assertEqual(result["calendar"]["day_boundary"], "23:00")
                self.assertEqual(result["calendar"]["pillar_source"], "time")

    def test_sixty_day_void_and_spirit_tables(self):
        stems, branches = "甲乙丙丁戊己庚辛壬癸", "子丑寅卯辰巳午未申酉戌亥"
        empty_by_xun = ["戌亥", "申酉", "午未", "辰巳", "寅卯", "子丑"]
        empty_by_day = {stems[i % 10] + branches[i % 12]: empty_by_xun[i // 10] for i in range(60)}
        spirits = ["青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"]
        starts = dict(zip(stems, [0, 0, 1, 1, 2, 3, 4, 4, 5, 5], strict=True))
        seen = set()
        for offset in range(60):
            result = chart(DEFAULT_TIME + timedelta(days=offset), line_values=[7] * 6)
            day = result["bazi"].split()[2]
            seen.add(day)
            self.assertEqual(result["kongwang"], empty_by_day[day])
            start = starts[day[0]]
            self.assertEqual([result[f"yao_{i}"]["liushen"] for i in range(1, 7)], spirits[start:] + spirits[:start])
        self.assertEqual(len(seen), 60)

    def test_rules_are_explicit_and_do_not_touch_global_provider(self):
        dt = datetime(2026, 9, 16, 23)
        poison = unittest.mock.Mock()
        poison.get_eight_char.side_effect = AssertionError("global provider must not be consulted")
        rules = ["default_next_day", "lunar_sect2_day_same"] * 10

        def calculate(rule):
            return chart(dt, cnts=[1] * 6, calc_rules={"zi_hour": rule})

        with patch.object(LunarHour, "provider", poison):
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(calculate, rules))
            self.assertEqual(str(create_four_pillars(dt).day), "甲午")
            self.assertIs(LunarHour.provider, poison)
        for rule, result in zip(rules, results, strict=True):
            next_day = rule == "default_next_day"
            self.assertEqual(result["bazi"].split()[2], "甲午" if next_day else "癸巳")
            self.assertEqual(result["kongwang"], "辰巳" if next_day else "午未")
            self.assertEqual(result["yao_1"]["liushen"], "青龙" if next_day else "玄武")
            self.assertEqual(result["calendar"]["day_boundary"], "23:00" if next_day else "00:00")
            self.assertEqual(result["calendar"]["zi_hour"], rule)
        poison.get_eight_char.assert_not_called()

    def test_bad_calendar_rules_and_aware_time_fail(self):
        for rules in ({"zi_hour": "invalid"}, {"timezone": "UTC"}, []):
            with self.subTest(rules=rules), self.assertRaises(ValueError):
                chart(cnts=[1] * 6, calc_rules=rules)
        for dt in (datetime(2026, 9, 16, tzinfo=timezone.utc), "2026-09-16"):
            with self.subTest(dt=dt), self.assertRaises(ValueError):
                chart(dt, cnts=[1] * 6)

    def test_provided_pillars_have_honest_provenance(self):
        bazi = create_bazi(datetime(2026, 9, 16, 23), calc_rules={"zi_hour": "lunar_sect2_day_same"})
        with patch("divicast.sixline.divinatory_symbol.create_bazi", side_effect=AssertionError("do not recalculate")):
            # 姤 needs a hidden line, so this also checks the subsidiary palace chart.
            result = chart(cnts=[2, 1, 1, 1, 1, 1], bazi=bazi)
        self.assertEqual(result["bazi"], str(bazi))
        self.assertEqual(result["calendar"], {"time_basis": "caller_normalized_naive", "pillar_source": "provided"})
        with self.assertRaises(ValueError):
            chart(cnts=[1] * 6, bazi=bazi, calc_rules={"zi_hour": "default_next_day"})

    def test_schema_and_legacy_json_compatibility(self):
        output = to_standard_format(DivinatorySymbol.create([0, 1, 2, 3, 0, 1], DEFAULT_TIME))
        schema = StandardDivinatorySymbolOutput.model_json_schema()
        snapshot = json.loads((Path(__file__).parents[1] / "src/divicast/sixline/schema.json").read_text())
        self.assertEqual(snapshot, schema)
        validate(output.model_dump(), schema)
        validate(output.model_dump(mode="json", exclude_none=True), schema)
        legacy = old_fields(output.model_dump(mode="json", exclude_none=True))
        restored = StandardDivinatorySymbolOutput.model_validate(legacy)
        self.assertIsNone(restored.casting)
        self.assertIsNone(restored.calendar)
        for invalid in ([1] * 5, [1] * 7, [True] * 6, [1.0] * 6, [4] * 6):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                StandardDivinatorySymbolOutput.model_validate(legacy | {"yaogua": invalid})
