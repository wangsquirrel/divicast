from divicast.base.symbol import ValuedMultiton
from divicast.entities.wuxing import Wuxing


class Relative(ValuedMultiton):
    """
    六亲
    """

    Brother = (0, "兄弟")
    Descendant = (1, "子孙")
    Parent = (2, "父母")
    Governer = (3, "官鬼")
    Wife = (4, "妻财")
