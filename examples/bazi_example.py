import datetime

from divicast.birth_chart.birth import BirthChart, Gender
from divicast.birth_chart.output import plain_draw_chart, to_standard_format

# 创建命盘。
# 传入时间必须是调用方已经归一化好的排盘时间，并且必须是 naive datetime。
# 如果你的业务口径是当地真太阳时，应先在调用方完成转换，再传入本库。
bc = BirthChart.create(
    datetime.datetime(1990, 8, 15, 14, 30, 0),
    gender=Gender.Male,
    # 可通过 calc_rules["zi_hour"] 切换晚子时口径：
    # "lunar_sect2_day_same"（默认，23:00-23:59 日柱算当天）
    # "default_next_day"（23:00-23:59 日柱算次日）
)

# 打印命盘
plain_draw_chart(bc)

# 目标时间同样必须与出生时间使用同一排盘时间口径。
target_dt = datetime.datetime(2025, 3, 4, 12, 0, 0)

# 输出标准格式 JSON
print("\n=== 标准 JSON 输出 ===")
standard_output = to_standard_format(bc, target_dt)
print(standard_output.model_dump_json(exclude_none=True, indent=2))

# 输出 JSON Schema
print("\n=== JSON Schema ===")
print(standard_output.model_json_schema())
