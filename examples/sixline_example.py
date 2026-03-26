import datetime

from divicast.sixline import DivinatorySymbol, plain_draw_divination, rich_draw_divination, to_standard_format

# 显式传入起卦时间。
# 传入时间必须是调用方已经归一化好的排盘时间，并且必须是 naive datetime。
d = DivinatorySymbol.create(
    [1, 3, 0, 1, 0, 0],
    datetime.datetime(2024, 6, 11, 14, 5, 0),
)

# 不传时间时，默认取当前本地 naive datetime。
d = DivinatorySymbol.create(None, None)

rich_draw_divination(d)
print(plain_draw_divination(d))

print(to_standard_format(d).model_dump_json(exclude_none=True))
# print(to_standard_format(d).model_json_schema())
