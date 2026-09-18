# 玄学排盘库 [![CI](https://github.com/wangsquirrel/divicast/actions/workflows/ci.yml/badge.svg)](https://github.com/wangsquirrel/divicast/actions/workflows/ci.yml) [![License](https://img.shields.io/badge/license-MIT-4EB1BA.svg?style=flat-square)](https://github.com/wangsquirrel/divicast/blob/main/LICENSE)

本库用于六爻排盘（六爻预测）和八字排盘（八字预测），提供了基础的六爻、八字相关实体、符号、五行、天干地支等数据结构和推演逻辑，适合用于命理、易学、占卜等相关应用的开发。致力于面向未来，面向AI

## 功能简介

### 六爻排盘
- 支持六爻排盘的基本流程
- 内置天干、地支、五行、六神、卦象等基础数据
- 提供六爻相关实体和符号的操作

### 八字排盘
- 支持八字排盘的基本流程
- 提供格局、大运、流年、神煞等分析功能
- 内置十神、纳音、十二长生等基础数据

## 安装

```bash
pip install divicast
```

或直接克隆仓库：
```
git clone https://github.com/wangsquirrel/divicast.git
cd divicast
pip install .
```

## 快速上手

以下是一个简单的六爻排盘示例：

更多用法请参考 examples/sixline_example.py。

```python
from divicast.sixline import DivinatorySymbol, rich_draw_divination, to_standard_format

# 创建一个六爻卦象
d = DivinatorySymbol.create()

# 输出文本排版格式的卦象
rich_draw_divination(d)

# 输出卦象标准化json格式
print(to_standard_format(d).model_dump_json(exclude_none=True))
```

从 0.2.4 起，新调用推荐使用标准爻值，顺序为初爻到上爻：

```python
from datetime import datetime

d = DivinatorySymbol.create(
    now=datetime(2026, 2, 4, 4, 30, 0),
    line_values=[6, 7, 8, 9, 6, 7],
    calc_rules={"zi_hour": "default_next_day"},
)
# 同一盘的传统铜钱字面计数：
d = DivinatorySymbol.create(
    now=datetime(2026, 2, 4, 4, 30, 0),
    coin_counts=[3, 2, 1, 0, 3, 2], coin_side="text",
)
```

`line_values` 中 6 老阴、7 少阳、8 少阴、9 老阳。`coin_side` 必须指定为 `text`
（字面）或 `back`（背面）；三种输入互斥。旧 `cnts` 和 JSON `yaogua` 仍保持原来的
0–3 编码，**不表示传统铜钱字面枚数**。空列表和非法输入会报错，只有未提供记录时才随机。
输出新增 `line_values`、`casting` 和 `calendar`，供 CLI、MCP 和 Python 调用统一消费。
详见[六爻模块说明](docs/sixline_module.md)。

### 八字

以下是一个简单的八字排盘示例：

更多用法请参考 examples/bazi_example.py。

```python
import datetime
from divicast.birth_chart import BirthChart, Gender

# 创建一个八字盘
chart = BirthChart.create(
    datetime.datetime(1990, 8, 15, 14, 30, 0),
    gender=Gender.Male,
)

# 输出八字标准化json格式
print(chart.to_standard_output().model_dump_json(exclude_none=True))
```

## 时间约定

- 本库不处理时区、地点、真太阳时换算。
- 传入 `BirthChart.create()`、`to_standard_format()`、`DivinatorySymbol.create()` 的时间，必须是调用方已经归一化好的排盘时间。
- 当前只接受 `naive datetime`。如果传入带 `tzinfo` 的 aware `datetime`，库会直接拒绝。
- 如果你的业务口径是“当地真太阳时排盘”，请先在调用方完成转换，再把转换后的 `naive datetime` 传入本库。
- 六爻和共享四柱函数完整保留分秒，默认立春换年、十二节换月、23 点换日；
  `calc_rules={"zi_hour": "lunar_sect2_day_same"}` 可选择 Tyme 流派 2 的日界，
  不依赖全局 provider。八字现有默认流派不变。
- tyme 节气时刻以 UTC+08:00 为基准。仅提供当地无时区时间并不等于完成了当地节气
  换算，调用方须明确口径；本库不做当地节气或真太阳时自动校正。

如有问题或建议，欢迎提交 issue 或 PR
