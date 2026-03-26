from divicast.base.symbol import ValuedMultiton


class Gender(ValuedMultiton):
    """性别"""

    Female = (0, "女")
    Male = (1, "男")
