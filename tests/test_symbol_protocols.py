import unittest

from divicast.birth_chart.birth import ZhuInfo
from divicast.entities.ganzhi import Dizhi, Nayin, SixtyJiazi, Tiangan
from divicast.entities.misc import Gender
from divicast.entities.protocols import HasGanzhi, HasWuxing, HasYinYang
from divicast.entities.trigram import Trigram
from divicast.entities.wuxing import Wuxing
from divicast.time_utils import create_kongwang


class TestSymbolProtocols(unittest.TestCase):
    def test_existing_symbols_satisfy_wuxing_without_protocol_inheritance(self) -> None:
        for symbol_type in (Tiangan, Dizhi, Trigram, Nayin):
            for member in symbol_type:
                with self.subTest(member=member):
                    self.assertIsInstance(member, HasWuxing)
                    self.assertIsInstance(member.wuxing, Wuxing)
        self.assertNotIsInstance(Gender.Male, HasWuxing)
        self.assertNotIsInstance(object(), HasWuxing)

    def test_yinyang_capability_is_independent_of_wuxing(self) -> None:
        for symbol_type in (Tiangan, Dizhi, Gender):
            for member in symbol_type:
                with self.subTest(member=member):
                    self.assertIsInstance(member, HasYinYang)
        self.assertNotIsInstance(Trigram.Qian, HasYinYang)
        self.assertNotIsInstance(Nayin.HaiZhongJin, HasYinYang)
        self.assertNotIsInstance(object(), HasYinYang)

    def test_runtime_check_does_not_evaluate_properties(self) -> None:
        class LazySymbol:
            @property
            def wuxing(self) -> Wuxing:
                raise AssertionError("Capability checks must not evaluate this property")

        self.assertIsInstance(LazySymbol(), HasWuxing)

    def test_runtime_check_does_not_validate_result_types(self) -> None:
        class IncorrectSymbol:
            @property
            def wuxing(self) -> str:
                return "木"

        # Static type checking rejects this as a HasWuxing argument; isinstance
        # only checks member presence, so it cannot validate the result type.
        self.assertIsInstance(IncorrectSymbol(), HasWuxing)

    def test_all_sixty_days_work_with_value_and_chart_pillar(self) -> None:
        xun_kongwang = ("戌亥", "申酉", "午未", "辰巳", "寅卯", "子丑")
        for index in range(60):
            gan, zhi = Tiangan(index % 10), Dizhi(index % 12)
            value = SixtyJiazi(gan, zhi)
            for day in (value, ZhuInfo(value, day_master=gan, shensha=())):
                with self.subTest(day=str(value), container=type(day).__name__):
                    self.assertIsInstance(day, HasGanzhi)
                    self.assertEqual(xun_kongwang[index // 10], "".join(map(str, create_kongwang(day))))

    def test_ganzhi_protocol_accepts_an_independent_object(self) -> None:
        class DayPillar:
            gan = Tiangan.Jia
            zhi = Dizhi.Zi

        day = DayPillar()
        self.assertIsInstance(day, HasGanzhi)
        self.assertEqual((Dizhi.Xu, Dizhi.Hai), create_kongwang(day))
        self.assertNotIsInstance(Tiangan.Jia, HasGanzhi)
        self.assertNotIsInstance(object(), HasGanzhi)
