from __future__ import annotations

from collections.abc import Iterator
from enum import Enum, EnumMeta
from typing import Any, Self, cast

from typing_extensions import deprecated


class MetaphysicalSymbolMeta(EnumMeta):
    """Resolve member names first, then Chinese names, using the existing [] API."""

    def __getitem__(cls, name: str) -> Any:
        # As with EnumMeta, the result belongs to the concrete enum subclass.
        try:
            return super().__getitem__(name)
        except KeyError:
            symbol_type = cast("type[MetaphysicalSymbol]", cls)
            for member in symbol_type:
                if member.chinese_name == name:
                    return member
            raise


class MetaphysicalSymbol(Enum, metaclass=MetaphysicalSymbolMeta):
    """命理术数中的有限符号，具有整数编码和中文名称。

    成员以 ``(编码, 中文名)`` 定义；子类可以附加其他成员数据。
    ``X(0)`` 按编码查找，``X["Jia"]`` 和 ``X["甲"]`` 按名称查找。
    成员保持 Enum 的相等语义；需要数字时使用 ``int(member)`` 或 ``member.num``。
    循环遍历遵循声明顺序。五行、阴阳等具体关系由相应子类的只读属性表达。
    """

    def __init__(self, num: int, chinese_name: str) -> None:
        if type(num) is not int or not isinstance(chinese_name, str):
            raise TypeError("Enum members must be defined as a tuple of (int, str).")

    @property
    def num(self) -> int:
        """只读整数编码；保留成员原有的元组 value。"""
        return cast(int, self.value[0])

    @property
    def chinese_name(self) -> str:
        """只读中文名称。"""
        return cast(str, self.value[1])

    @classmethod
    def _missing_(cls, value: object) -> Self | None:
        """Support integer codes without treating bool as an integer code."""
        if type(value) is int:
            for member in cls:
                if member.num == value:
                    return member
        return None

    @classmethod
    @deprecated('改用 cls["chinese_name"]')
    def from_chinese_name(cls, chinese_name: str) -> Self:
        """按中文名查找；兼容旧接口及其 ValueError 约定。"""
        for member in cls:
            if member.chinese_name == chinese_name:
                return member
        raise ValueError(f"'{chinese_name}' is not a valid chinese_name for {cls.__name__}")

    @classmethod
    def all(cls) -> list[Self]:
        """返回按声明顺序排列的成员列表。"""
        return list(cls)

    def next(self, step: int = 1) -> Self:
        """按声明顺序循环移动，支持负数和跨多圈步长。"""
        if type(step) is not int:
            raise TypeError("step must be an integer")
        members = type(self).all()
        index = members.index(self)
        return members[(index + step) % len(members)]

    @classmethod
    def iterator_from(cls, start_member: Self) -> Iterator[Self]:
        """从指定成员开始，按声明顺序遍历一圈。"""
        if not isinstance(start_member, cls):
            raise TypeError(f"start_member must be an instance of {cls.__name__}")
        members = cls.all()
        start = members.index(start_member)
        yield from members[start:]
        yield from members[:start]

    def __str__(self) -> str:
        return self.chinese_name

    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}: {self.num} ('{self.chinese_name}')>"

    def __int__(self) -> int:
        return self.num

    def __hash__(self) -> int:
        # Preserve existing set traversal in chart calculations. Collisions between
        # different enum types are valid: equality still distinguishes the members.
        return hash(self.num)

    @deprecated("Use .name instead; to_dict() returns a member name, not a dictionary.")
    def to_dict(self) -> str:
        """返回成员名称；保留旧返回值，推荐直接读取 name。"""
        return self.name
