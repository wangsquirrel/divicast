# 符号、干支与四柱领域对象

六爻和八字共用两个基础值对象：

- `divicast.entities.ganzhi.SixtyJiazi`：一个合法的六十甲子干支。
- `divicast.entities.pillars.FourPillars`：按年、月、日、时定位的四个 `SixtyJiazi`。

两者都是 `frozen=True, slots=True` 的 dataclass，按值比较、可哈希，适合用作字典键。
构造时会检查类型；`SixtyJiazi` 还会检查天干与地支的阴阳配对。

## 符号与能力协议

`MetaphysicalSymbol` 是命理术数符号的枚举基类，保留整数编码查找、中文名查找
和 `next()` 循环遍历。`num`、`chinese_name` 为只读属性，成员的元组 `value`
保持原值。成员采用 Enum 的相等语义，不再等于整数或其他枚举类型的同编码成员；
需要编码时显式读取 `.num` 或使用 `int(member)`。

`next()` 按声明顺序移动，支持负数和跨多圈步长。五行、阴阳等关系由相应类型
提供 `.wuxing`、`.yinyang` 属性；干支关系模式提供 `.relation_type`、`.position_kind`。
基类不再注册通用的 `belongs_to` 关系。

调用方按所需能力标注 `HasWuxing`、`HasYinYang` 或 `HasGanzhi`，具体对象无需
继承这些协议：

```python
from divicast.entities.ganzhi import Tiangan
from divicast.entities.protocols import HasWuxing
from divicast.entities.wuxing import Wuxing


def element_of(symbol: HasWuxing) -> Wuxing:
    return symbol.wuxing


assert element_of(Tiangan.Jia) is Wuxing.Wood
```

协议支持 `isinstance`，但运行时检查只确认成员存在，不验证返回值类型或领域合法性。

## 构造和使用

```python
from dataclasses import replace

from divicast.entities.ganzhi import Dizhi, SixtyJiazi, Tiangan
from divicast.entities.pillars import FourPillars

day = SixtyJiazi(Tiangan.Bing, Dizhi.Wu)
assert day == SixtyJiazi.parse("丙午")

pillars = FourPillars(
    year=SixtyJiazi.parse("甲辰"),
    month=SixtyJiazi.parse("庚午"),
    day=day,
    hour=SixtyJiazi.parse("乙未"),
)
assert str(pillars) == "甲辰 庚午 丙午 乙未"
assert pillars.day is day

# 遍历顺序固定为年、月、日、时。
assert tuple(pillars) == (pillars.year, pillars.month, pillars.day, pillars.hour)

# 修改某柱时创建新值，原值保持不变；replace 同样执行构造校验。
other = replace(pillars, day=SixtyJiazi.parse("丁未"))
assert other != pillars
```

`FourPillars` 表达四柱的值。它不保存历法规则、出生时间、性别或分析结果，
也不验证四柱之间的历法对应关系、保证其对应某个实际时刻。

## 历法边界和排盘入口

```python
from datetime import datetime

from divicast.birth_chart.birth import BirthChart
from divicast.entities.misc import Gender
from divicast.sixline import DivinatorySymbol
from divicast.time_utils import create_four_pillars

dt = datetime(2026, 9, 16, 23)
rules = {"zi_hour": "lunar_sect2_day_same"}
pillars = create_four_pillars(dt, calc_rules=rules)

birth_chart = BirthChart(dt, Gender.Male, calc_rules=rules)
assert birth_chart.pillars == pillars
assert birth_chart.dayzhu.sixty_jiazi is birth_chart.pillars.day
assert birth_chart.chart_analysis.geju.geju is not None

sixline = DivinatorySymbol.create(now=dt, line_values=[7] * 6, bazi=pillars)
assert sixline.bazi is pillars
assert sixline.calendar.pillar_source == "provided"
```

`BirthChart(...)` 和 `BirthChart.create(...)` 都在返回前完成盘面装配和分析。
`create()` 委托构造函数，不重复计算。调用方无需再调用 `assemble()`、`analyze()`；
这两个方法仍可显式调用，但不再是创建命盘的必需步骤。

`create_four_pillars()` 负责调用历法，并返回领域 `FourPillars`。
已有 Tyme `EightChar` 时，使用 `four_pillars_from_tyme()` 转换；该适配函数
不重新排历法、不选择流派，也不修改全局 provider。领域对象不依赖 Tyme。

各入口的既有默认规则保持如下：

| 入口 | 默认 `zi_hour` |
| --- | --- |
| `create_four_pillars()`、六爻时间起盘 | `default_next_day`：23 点换日 |
| `BirthChart(...)`、`BirthChart.create()` | `lunar_sect2_day_same`：晚子时日柱仍属当天 |

两个系统使用相同时间和明确的相同规则时，得到相等的四柱值。
六爻显式传入 `bazi=FourPillars(...)` 时，不能同时传入 `calc_rules`；
其来源仍标记为 `provided`，不声称它由显示时间推算。

## 命盘信息与输出

`ZhuInfo` 表达八字单柱的完整信息。构造时必须提供 `SixtyJiazi`、日主
`day_master` 和已计算的神煞 `shensha`，构造完成后即可读取主星、藏干、副星、
星运、自坐等属性，不需要逐项补充赋值。

```python
from divicast.birth_chart.birth import ZhuInfo

year_info = ZhuInfo(
    birth_chart.pillars.year,
    day_master=birth_chart.pillars.day.gan,
    shensha=birth_chart.yearzhu.shensha,
)
assert year_info.zhuxing == birth_chart.yearzhu.zhuxing
assert year_info.fuxing == birth_chart.yearzhu.fuxing
```

`shensha` 接受有序的 `Daemon` 序列，构造时复制为独立列表并保留顺序。
空序列表示调用方明确提供“没有神煞”的结果，因此该参数没有默认值。
命盘构造时会先按现有规则计算整盘神煞，再传入对应各柱。

干支相关属性保持只读：
`sixty_jiazi`、`gan`、`zhi`、`nayin`、`kongwang`，这些属性均来自同一个干支值。
`ZhuInfo` 的其余字段和列表仍可修改；本轮只保证构造完整性，没有将整个命盘冻结。

`HasGanzhi` 继续用于只要求提供 `gan`、`zhi` 属性的通用函数。
它不保证六十甲子的合法性；需要这种保证时，接收 `SixtyJiazi`。

`birth_chart.output.FourPillars` 是另一个职责明确的 Pydantic 输出模型，
包含十神、藏干、神煞等结构化字段。通过各模块的 `to_standard_format()`
生成面向 AI 的输出，JSON 字段与 Schema 保持原有契约。

## Python API 迁移

本次移除了重复容器，没有保留旧类型别名。

| 原用法 | 当前用法 |
| --- | --- |
| `ValuedMultiton`、`ValuedMultitonMeta` | `MetaphysicalSymbol`、`MetaphysicalSymbolMeta` |
| `symbol.belongs_to(Wuxing)`、`symbol.belongs_to(YinYang)` | 支持该关系的类型使用 `.wuxing`、`.yinyang`；参数按能力协议标注 |
| `pattern.belongs_to(RelationType/GanZhi)` | `.relation_type`、`.position_kind` |
| `symbol == 0`、跨枚举比较同编码成员 | 明确比较 `.num`，或直接比较同类型枚举成员 |
| 给 `symbol.num/chinese_name` 赋值 | 成员元数据只读，需要其他值时选择对应成员 |
| `symbol.to_dict()` | `.name`；旧方法仍返回成员名，但已弃用 |
| `time_utils.GanzhiPair(gan, zhi)` | `entities.ganzhi.SixtyJiazi(gan, zhi)` |
| `sixline.divinatory_symbol.Ganzhi(gan, zhi)` | `entities.ganzhi.SixtyJiazi(gan, zhi)` |
| `sixline.divinatory_symbol.Bazi(...)` | `entities.pillars.FourPillars(...)` |
| 从 `time_utils` 导入 `FourPillars` | 从 `entities.pillars` 导入领域 `FourPillars` |
| `create_bazi(dt, calc_rules=...)` | `time_utils.create_four_pillars(dt, calc_rules=...)` |
| `Bazi(..., bihour=value)`、`bazi.bihour` | `FourPillars(..., hour=value)`、`bazi.hour` |
| `pair.as_sixty_jiazi()` | 已经是 `SixtyJiazi`，直接使用 |
| `ZhuInfo("甲子")` 或 `ZhuInfo(value)` | `ZhuInfo(value, day_master=日主天干, shensha=已计算的神煞)`；文本先用 `SixtyJiazi.parse()` 解析 |
| 给 `ZhuInfo.gan/zhi/sixty_jiazi/nayin/kongwang` 赋值 | 构造所需干支并创建新的柱信息 |
| `build_pillar_shensha(tyme_eight_char, gender)` | 传入领域 `FourPillars`，例如 `birth_chart.pillars` |
| `BirthChart(...)` 后手动调用 `assemble()`、`analyze()` | 直接构造或调用 `create()` 即得到完整命盘，可移除这两次重复调用 |

领域对象不再继承 tuple，不支持下标、切片、`_asdict()`、`_replace()` 或与普通
tuple 的相等比较。使用具名属性读取、`dataclasses.replace()` 创建修改后的值。
`FourPillars` 提供有序遍历，因此仍支持四柱解包；`SixtyJiazi` 使用 `.gan`、`.zhi` 读取。

六爻的 `bazi=` 参数和 `.bazi` 属性名称保留，其类型统一为领域 `FourPillars`；
八字通过 `.pillars` 读取同一类型，现有 `yearzhu/monthzhu/dayzhu/bihourzhu`
继续提供各柱的命盘信息。
