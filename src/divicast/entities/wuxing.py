from __future__ import annotations

from divicast.base.symbol import BelongsTo, ValuedMultiton


class YinYang(ValuedMultiton):
    """阴阳"""

    Yin = (0, "阴")
    Yang = (1, "阳")


class BelongsToYinYang(BelongsTo):
    """
    实现了`BelongsTo`接口的类，表示属于某个阴阳
    通过定义`_YINYANG_MAP`，可以自动返回所属阴阳
    """

    def belongs_to_yinyang(self) -> YinYang:
        """
        默认实现，通过定义`_YINYANG_MAP`，返回所属阴阳
        """
        return self.belongs_to(YinYang, "_YINYANG_MAP")


class Wuxing(ValuedMultiton):
    """五行"""

    Wood = (0, "木")
    Fire = (1, "火")
    Earth = (2, "土")
    Metal = (3, "金")
    Water = (4, "水")

    def restrain(self) -> Wuxing:
        """
        表示五行相克
        """
        return Wuxing((self.num + 2) % 5)

    def generate(self) -> Wuxing:
        """
        表示五行相生
        """
        return Wuxing((self.num + 1) % 5)


class BelongsToWuxing(BelongsTo):
    """
    这是一个协议，它定义了一个“可以转化为五行”的契约。
    """

    def belongs_to_wuxing(
        self,
    ) -> Wuxing:
        return self.belongs_to(Wuxing, "_WUXING_MAP")
