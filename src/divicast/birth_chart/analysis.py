from divicast.base.symbol import ValuedMultiton


class Strength(ValuedMultiton):
    """表示实体强弱的枚举"""

    VERY_WEAK = (0, "极弱")
    WEAK = (1, "弱")
    NEUTRAL = (2, "中性")
    STRONG = (3, "强")
    VERY_STRONG = (4, "极强")
