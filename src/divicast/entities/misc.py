from divicast.base.symbol import MetaphysicalSymbol
from divicast.entities.wuxing import YinYang


class Gender(MetaphysicalSymbol):
    """性别"""

    Female = (0, "女")
    Male = (1, "男")

    @property
    def yinyang(self) -> YinYang:
        """本库起运规则采用的性别阴阳对应：男阳、女阴。"""
        return _GENDER_YINYANG[self]


_GENDER_YINYANG: dict[Gender, YinYang] = {Gender.Female: YinYang.Yin, Gender.Male: YinYang.Yang}
