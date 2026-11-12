"""领域能力协议：对象按结构满足接口，无需继承这些协议。

运行时 isinstance 检查只确认成员存在，不验证其返回值类型或领域合法性。
"""

from typing import Protocol, runtime_checkable

from divicast.entities.ganzhi import Dizhi, Tiangan
from divicast.entities.wuxing import Wuxing, YinYang

__all__ = ["HasGanzhi", "HasWuxing", "HasYinYang"]


@runtime_checkable
class HasWuxing(Protocol):
    """提供所属五行的对象。"""

    @property
    def wuxing(self) -> Wuxing: ...


@runtime_checkable
class HasYinYang(Protocol):
    """提供阴阳属性的对象。"""

    @property
    def yinyang(self) -> YinYang: ...


@runtime_checkable
class HasGanzhi(Protocol):
    """提供天干、地支的对象；不要求具体的干支容器类型。"""

    @property
    def gan(self) -> Tiangan: ...

    @property
    def zhi(self) -> Dizhi: ...
