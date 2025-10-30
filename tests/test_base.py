
import unittest
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


class TestEntity(unittest.TestCase):
    def test_b5_entity(self):
        a = EntityWithNameTest(1)
        b = EntityWithNameTest(2)
        self.assertIs(EntityWithNameTest(1), EntityWithNameTest(1))
        self.assertIs(EntityWithNameTest.A, EntityWithNameTest.A)
        self.assertIs(EntityWithNameTest(1), EntityWithNameTest.A)
        self.assertEqual("B", b.name)
        self.assertEqual(2, b.num)
        self.assertEqual(2, b)
        self.assertEqual("b", b.chinese_name)

        self.assertEqual(len(EntityWithNameTest), 6)

        self.assertEqual("A", EntityWithNameTest(1).name)
        self.assertEqual(1, EntityWithNameTest(1).num)

        with self.assertRaises(ValueError) as context:
            EntityWithNameTest(9)

        self.assertIs(EntityWithNameTest(2), EntityWithNameTest(2))
        self.assertIs(EntityWithNameTest["B"], EntityWithNameTest(2))
        self.assertIs(EntityWithNameTest.B, EntityWithNameTest(2))
        self.assertIs(EntityWithNameTest.B,
                      EntityWithNameTest.from_chinese_name("b"))
        self.assertEqual(
            EntityWithNameTest.A, EntityWithNameTest.from_chinese_name("a")
        )
        self.assertEqual(EntityWithNameTest.A, EntityWithNameTest(1))

        self.assertEqual(EntityWithNameTest.B, a.next())
        self.assertEqual(EntityWithNameTest.C, a.next().next())
        self.assertEqual(EntityWithNameTest.F, a.next().next().next())
        self.assertEqual(EntityWithNameTest.d, a.next().next().next().next())
        self.assertEqual(EntityWithNameTest._e,
                         a.next().next().next().next().next())
        self.assertEqual(EntityWithNameTest.A,
                         a.next().next().next().next().next().next())

        it = Tiangan.iterator_from(Tiangan.Yi)
        for i in it:
            print(i, '-')

    def test_b6_entity(self):

        class EntityWithoutNameTest(ValuedMultiton):
            pass

        with self.assertRaises(TypeError):
            EntityWithoutNameTest('a')

        with self.assertRaises(TypeError):

            class DuplicateValue2(ValuedMultiton):
                JUST_AN_INT = 100  # 这报错
