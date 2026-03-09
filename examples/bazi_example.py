import datetime

from divicast.birth_chart.birth import BirthChart, Gender
from divicast.birth_chart.output import plain_draw_chart, to_standard_format

# 创建命盘：1990年8月15日 14:30:00 男性
bc = BirthChart.create(
    datetime.datetime(1990, 8, 15, 14, 30, 0),
    gender=Gender.MAN,
)

# 打印命盘
#plain_draw_chart(bc)

# 目标时间：用于计算流年流月
target_dt = datetime.datetime(2025, 3, 4, 12, 0, 0)

# 输出标准格式 JSON
print("\n=== 标准 JSON 输出 ===")
standard_output = to_standard_format(bc, target_dt)
print(standard_output.model_dump_json(exclude_none=True, indent=2))

# 输出 JSON Schema
print("\n=== JSON Schema ===")
print(standard_output.model_json_schema())
