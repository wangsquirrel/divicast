import datetime

from divicast.sixline import DivinatorySymbol, plain_draw_divination, rich_draw_divination, to_standard_format

# 显式传入起卦时间。
# 传入时间必须是调用方已经归一化好的排盘时间，并且必须是 naive datetime。
d = DivinatorySymbol.create(
    now=datetime.datetime(2024, 6, 11, 14, 5, 0),
    line_values=[7, 9, 6, 7, 6, 6],
    calc_rules={"zi_hour": "default_next_day"},
)

# 传统字面枚数可改用 coin_counts=[2, 0, 3, 2, 3, 3], coin_side="text"。
# 旧 cnts=[1, 3, 0, 1, 0, 0] 编码仍兼容，但不应称为传统字面枚数。
# 不传记录时才随机；不传时间时使用当前本地 naive datetime。

rich_draw_divination(d)
print(plain_draw_divination(d))

print(to_standard_format(d).model_dump_json(exclude_none=True))
# print(to_standard_format(d).model_json_schema())
