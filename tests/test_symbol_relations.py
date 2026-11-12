import unittest

from divicast.birth_chart.analysis_enums import GanZhi
from divicast.birth_chart.relation_models import RelationPattern, RelationType
from divicast.entities.ganzhi import Dizhi, Nayin, Tiangan
from divicast.entities.misc import Gender
from divicast.entities.trigram import Trigram
from divicast.entities.wuxing import Wuxing, YinYang


class TestSymbolRelations(unittest.TestCase):
    def test_wuxing_properties_cover_each_symbol(self):
        cases = (
            (Tiangan, "木木火火土土金金水水"),
            (Dizhi, "水土木木土火火土金金土水"),
            (Trigram, "土木水金土火木金"),
            (Nayin, "金火木土金火水土金木水土火木水金火木土金火水土金木水土火木水"),
        )
        for symbol_type, expected in cases:
            with self.subTest(symbol_type=symbol_type.__name__):
                self.assertEqual(len(expected), len(symbol_type))
                self.assertEqual(expected, "".join(str(member.wuxing) for member in symbol_type))
                for member in symbol_type:
                    self.assertIsInstance(member.wuxing, Wuxing)

    def test_yinyang_properties_preserve_the_existing_correspondences(self):
        cases = ((Tiangan, "阳阴阳阴阳阴阳阴阳阴"), (Dizhi, "阳阴阳阴阳阴阳阴阳阴阳阴"), (Gender, "阴阳"))
        for symbol_type, expected in cases:
            with self.subTest(symbol_type=symbol_type.__name__):
                self.assertEqual(expected, "".join(str(member.yinyang) for member in symbol_type))
                for member in symbol_type:
                    self.assertIsInstance(member.yinyang, YinYang)

    def test_relation_patterns_expose_type_and_position(self):
        self.assertEqual("冲合刑冲合害破合会刑刑", "".join(str(pattern.relation_type) for pattern in RelationPattern))
        for pattern in RelationPattern:
            with self.subTest(pattern=pattern.name):
                self.assertIsInstance(pattern.relation_type, RelationType)
                expected_position = (
                    GanZhi.TIANGAN
                    if pattern in (RelationPattern.TIANGAN_CHONG, RelationPattern.TIANGAN_WU_HE)
                    else GanZhi.DIZHI
                )
                self.assertIs(expected_position, pattern.position_kind)

    def test_relationship_properties_are_read_only(self):
        cases = (
            (Tiangan.Jia, "wuxing", Wuxing.Fire),
            (Tiangan.Jia, "yinyang", YinYang.Yin),
            (Dizhi.Zi, "wuxing", Wuxing.Fire),
            (Dizhi.Zi, "yinyang", YinYang.Yin),
            (Trigram.Qian, "wuxing", Wuxing.Fire),
            (Nayin.HaiZhongJin, "wuxing", Wuxing.Fire),
            (Gender.Male, "yinyang", YinYang.Yin),
            (RelationPattern.TIANGAN_CHONG, "relation_type", RelationType.HE),
            (RelationPattern.TIANGAN_CHONG, "position_kind", GanZhi.DIZHI),
        )
        for member, attribute, other_value in cases:
            with self.subTest(member=member, attribute=attribute):
                before = getattr(member, attribute)
                with self.assertRaises(AttributeError):
                    setattr(member, attribute, other_value)
                self.assertIs(before, getattr(member, attribute))

    def test_relative_relations_still_take_an_explicit_reference(self):
        self.assertEqual("正财", str(Tiangan.Jia.get_shishen(Tiangan.Ji)))
        self.assertEqual("正官", str(Tiangan.Ji.get_shishen(Tiangan.Jia)))
        self.assertIs(Wuxing.Fire, Wuxing.Wood.generate())
        self.assertIs(Wuxing.Earth, Wuxing.Wood.restrain())
