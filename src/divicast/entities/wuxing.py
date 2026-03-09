from __future__ import annotations

from divicast.base.symbol import ValuedMultiton


class YinYang(ValuedMultiton):
    """阴阳"""

    Yin = (0, "阴")
    Yang = (1, "阳")


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
