from enum import Enum
from typing import Any, Iterator, List, Self, Type, TypeVar

T = TypeVar("T", bound="ValuedMultiton")


class ValuedMultiton(Enum):
    """
    一个功能丰富的枚举基类，旨在通过继承来使用。

    它提供了多种方式来定义和访问枚举成员，每个成员都包含一个整数值和一个中文描述。

    特性:
    - 通过 `(整数, "中文名")` 的元组形式来定义成员。
    - 实例可以通过名称、整数值或中文名进行检索。
    - 提供了清晰的 `__str__` 和 `__repr__` 表示。
    - 支持迭代、比较，并提供了 `next()` 方法用于循环遍历。
    - 提供了 `all()` 和 `iterator_from()` 等便利的类方法。

    """

    def __init__(self, num: int, chinese_name: str | None = None):
        if not isinstance(num, int) or not isinstance(chinese_name, str):
            raise TypeError(
                "Enum members must be defined as a tuple of (int, str).")
        self.num = num
        self.chinese_name = chinese_name

    @classmethod
    def _missing_(cls: Type[T], value: Any) -> T | None:
        """
        实现通过整数值查找实例，例如 `Color(1)`。
        """
        if isinstance(value, int):
            for member in cls:
                if member.num == value:
                    return member
        return None

    @classmethod
    def from_chinese_name(cls: Type[T], chinese_name: str) -> T:
        """通过中文名查找枚举成员。"""
        for member in cls:
            if member.chinese_name == chinese_name:
                return member
        raise ValueError(
            f"'{chinese_name}' is not a valid chinese_name for {cls.__name__}"
        )

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        """以列表形式返回所有枚举成员，按定义顺序排列。"""
        return list(cls)

    def next(self, step: int = 1) -> Self:
        """返回后`step`个枚举成员。如果是最后一个，则循环回到第一个。"""
        members = self.all()
        index = members.index(self)
        return members[(index + step) % len(members)]

    @classmethod
    def iterator_from(cls: Type[T], start_member: T) -> Iterator[T]:
        """创建一个从指定成员开始并循环一次的迭代器。"""
        if not isinstance(start_member, cls):
            raise TypeError(
                f"start_member must be an instance of {cls.__name__}")

        current = start_member
        while True:
            yield current
            current = current.next()
            if current == start_member:
                break

    def __str__(self) -> str:
        """返回用户的友好字符串表示（中文名）。"""
        return self.chinese_name

    def __repr__(self) -> str:
        """返回开发者的清晰、无歧义的表示。"""
        return f"<{self.__class__.__name__}.{self.name}: {self.num} ('{self.chinese_name}')>"

    def __eq__(self, other: Any) -> bool:
        """
        允许枚举成员与整数值进行比较。
        例如 `Color.RED == 1`。
        """
        if isinstance(other, int):
            return self.num == other
        # 对于其他类型，使用 `enum.Enum` 的默认比较逻辑
        return super().__eq__(other)

    def __hash__(self) -> int:
        """确保枚举成员是可哈希的，以便在字典键或集合中使用。"""
        return hash(self.num)

    # --- 序列化 ---

    def to_dict(self) -> str:
        """
        返回一个简单的、可序列化的表示（成员名称）。
        """
        return self.name


class BelongsTo:
    """
    继承此类以创建一个属于另一个类的类。
    """

    def belongs_to(self, _: type[T], map_name: str) -> T:
        a = getattr(self, map_name)[self]
        return a
