import pickle
import unittest

from divicast.base.symbol import MetaphysicalSymbol
from divicast.entities.ganzhi import Tiangan
from divicast.entities.misc import Gender
from divicast.entities.wuxing import Wuxing


class EntityWithNameTest(MetaphysicalSymbol):
    A = (1, "a")
    B = (2, "b")
    C = (4, "c")
    F = (3, "f")  # 顺序问题

    d = (8, "d")
    _e = (16, "e")


class RoundEntity(MetaphysicalSymbol):
    AA = (1, "aa")
    BB = (2, "bb")
    CC = (3, "cc")
    DD = (4, "dd")
    EE = (5, "ee")
    FF = (6, "ff")


class TestEntity(unittest.TestCase):
    def test_b5_entity(self):
        a = EntityWithNameTest(1)
        b = EntityWithNameTest(2)
        self.assertEqual("B", b.name)
        self.assertEqual(2, b.num)
        self.assertEqual(2, int(b))
        self.assertNotEqual(2, b)
        self.assertEqual("b", b.chinese_name)
        self.assertEqual(len(EntityWithNameTest), 6)
        with self.assertRaises(ValueError):
            EntityWithNameTest(9)

        self.assertIs(EntityWithNameTest(2), EntityWithNameTest(2))
        self.assertIs(EntityWithNameTest.B, EntityWithNameTest["b"])
        self.assertIs(EntityWithNameTest.B, EntityWithNameTest["B"])
        self.assertIs(EntityWithNameTest.B, EntityWithNameTest(2))
        self.assertWarnsRegex(DeprecationWarning, r"改用 cls", EntityWithNameTest.from_chinese_name, "b")

        self.assertEqual(EntityWithNameTest.A, EntityWithNameTest["a"])
        self.assertEqual(EntityWithNameTest.A, EntityWithNameTest["A"])
        self.assertEqual(EntityWithNameTest.A, EntityWithNameTest(1))

        self.assertEqual(EntityWithNameTest.B, a.next())
        self.assertEqual(EntityWithNameTest.C, a.next().next())
        self.assertEqual(EntityWithNameTest.F, a.next().next().next())
        self.assertEqual(EntityWithNameTest.d, a.next().next().next().next())
        self.assertEqual(EntityWithNameTest._e, a.next().next().next().next().next())
        self.assertEqual(EntityWithNameTest.A, a.next().next().next().next().next().next())

        start = RoundEntity.BB
        it = RoundEntity.iterator_from(start)
        step = 0
        for i in it:
            self.assertEqual(i, RoundEntity((start.num - 1 + step) % len(RoundEntity) + 1))
            step += 1

    def test_b6_entity(self):

        class EntityWithoutNameTest(MetaphysicalSymbol):
            pass

        with self.assertRaises(TypeError):
            EntityWithoutNameTest("a")

        with self.assertRaises(TypeError):

            class DuplicateValue2(MetaphysicalSymbol):
                JUST_AN_INT = 100  # 这报错


class EntityWithMultiAttr(MetaphysicalSymbol):
    A = (1, "a", "extra_a")
    B = (2, "b", "extra_b")
    C = (4, "c", "extra_c")
    F = (3, "f", "extra_f")  # 顺序问题

    d = (8, "d", "extra_d")
    _e = (16, "e", "extra_e")

    def __init__(self, num, chinese_name, xxx: str):
        super().__init__(num, chinese_name)
        self.xxx = xxx


class TestEntityWithMultiAttr(unittest.TestCase):
    def test_multi_attr(self):
        self.assertEqual(EntityWithMultiAttr.A.xxx, "extra_a")
        self.assertEqual(EntityWithMultiAttr.B.chinese_name, "b")
        self.assertEqual(str(EntityWithMultiAttr.B), "b")


class TestMetaphysicalSymbol(unittest.TestCase):
    def test_equality_preserves_symbol_domains(self):
        self.assertNotEqual(Tiangan.Jia, Wuxing.Wood)
        self.assertNotEqual(Tiangan.Jia, 0)
        self.assertNotEqual(0, Tiangan.Jia)
        self.assertNotEqual(Gender.Male, True)
        self.assertNotEqual(Gender.Female, False)
        self.assertEqual(Tiangan.Jia, Tiangan(0))
        entries = {Tiangan.Jia: "stem", Wuxing.Wood: "element", 0: "integer"}
        self.assertEqual(3, len(entries))
        self.assertEqual("stem", entries[Tiangan(0)])

    def test_metadata_is_read_only_and_dictionary_keys_stay_valid(self):
        member = Tiangan.Jia
        entries = {member: "甲"}
        original_hash = hash(member)
        for name, value in (("num", 6), ("chinese_name", "庚")):
            with self.subTest(attribute=name):
                with self.assertRaises(AttributeError):
                    setattr(member, name, value)
                with self.assertRaises(AttributeError):
                    delattr(member, name)
        self.assertEqual(0, member.num)
        self.assertEqual("甲", member.chinese_name)
        self.assertEqual(original_hash, hash(member))
        self.assertEqual(hash(0), hash(member))
        self.assertEqual("甲", entries[Tiangan(0)])

    def test_lookup_and_serialization_keep_existing_contracts(self):
        member = Tiangan.Jia
        self.assertIs(member, Tiangan(0))
        self.assertIs(member, Tiangan((0, "甲")))
        self.assertIs(member, Tiangan["Jia"])
        self.assertIs(member, Tiangan["甲"])
        self.assertEqual((0, "甲"), member.value)
        self.assertEqual("甲", str(member))
        self.assertEqual("<Tiangan.Jia: 0 ('甲')>", repr(member))
        with self.assertWarnsRegex(DeprecationWarning, r"Use \.name"):
            self.assertEqual("Jia", member.to_dict())
        self.assertIs(member, pickle.loads(pickle.dumps(member)))
        self.assertEqual((1, "a", "extra_a"), EntityWithMultiAttr.A.value)
        self.assertIs(EntityWithMultiAttr.A, EntityWithMultiAttr((1, "a", "extra_a")))

    def test_invalid_lookup_values_are_rejected(self):
        for value in (True, False, 1.0, "甲", None, -1, 10):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Tiangan(value)
        with self.assertRaises(KeyError):
            Tiangan["不存在"]

    def test_boolean_member_codes_are_rejected(self):
        with self.assertRaises(TypeError):

            class InvalidSymbol(MetaphysicalSymbol):
                INVALID = (True, "无效")

    def test_member_names_take_precedence_over_chinese_names(self):
        class AmbiguousSymbol(MetaphysicalSymbol):
            FIRST = (0, "甲")
            SECOND = (1, "FIRST")

        self.assertIs(AmbiguousSymbol.FIRST, AmbiguousSymbol["FIRST"])
        with self.assertWarns(DeprecationWarning):
            self.assertIs(AmbiguousSymbol.SECOND, AmbiguousSymbol.from_chinese_name("FIRST"))

    def test_cycles_follow_declaration_order_instead_of_numeric_codes(self):
        members = EntityWithNameTest.all()
        self.assertEqual([1, 2, 4, 3, 8, 16], [member.num for member in members])
        for start, member in enumerate(members):
            for step in (0, 1, -1, len(members), 100, -100):
                with self.subTest(member=member, step=step):
                    self.assertIs(members[(start + step) % len(members)], member.next(step))
            self.assertEqual(members[start:] + members[:start], list(EntityWithNameTest.iterator_from(member)))
        copied_members = EntityWithNameTest.all()
        copied_members.clear()
        self.assertEqual(members, EntityWithNameTest.all())

    def test_invalid_cycle_arguments_are_rejected(self):
        for step in (True, 1.5, "1"):
            with self.subTest(step=step), self.assertRaises(TypeError):
                Tiangan.Jia.next(step)
        with self.assertRaises(TypeError):
            list(Tiangan.iterator_from(Wuxing.Wood))
