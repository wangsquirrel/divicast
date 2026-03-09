import unittest
from curses.ascii import FF
from typing import Literal

from divicast.base.symbol import ValuedMultiton
from divicast.entities.ganzhi import Tiangan


class EntityWithNameTest(ValuedMultiton):

    A = (1, "a")
    B = (2, "b")
    C = (4, "c")
    F = (3, "f")  # 顺序问题

    d = (8, "d")  # 这个属性会被忽略，因为不是大写开头
    _e = (16, "e")  # 这个属性会被忽略，因为以下划线开头


class RoundEntity(ValuedMultiton):

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
        self.assertEqual(2, b)
        self.assertEqual("b", b.chinese_name)
        self.assertEqual(len(EntityWithNameTest), 6)
        with self.assertRaises(ValueError) as context:
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

        class EntityWithoutNameTest(ValuedMultiton):
            pass

        with self.assertRaises(TypeError):
            EntityWithoutNameTest("a")

        with self.assertRaises(TypeError):

            class DuplicateValue2(ValuedMultiton):
                JUST_AN_INT = 100  # 这报错
