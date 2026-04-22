from divicast.base.symbol import ValuedMultiton
from divicast.entities.wuxing import YinYang


class Gender(ValuedMultiton):
    """性别"""

    Female = (0, "女")
    Male = (1, "男")


Gender._BELONGS_TO = {
    YinYang: {
        Gender.Female: YinYang.Yin,
        Gender.Male: YinYang.Yang,
    },
}
