# 八字排盘改动说明

本文件汇总本分支在八字排盘（`StandardBirthChartOutput`）上的改动点。

## 范围与原则

- 目标结构：`StandardBirthChartOutput`。
- 目的：补齐缺失字段，并尽量对齐主流排盘盘面字段。
- 对照基准：`https://github.com/yuhr123/bazi`。
- 仅实现一种流派；以注释和 `calc_rules` 保留扩展入口。

## 新增/补齐字段

- `lunar_birth`、`true_solar_birth`、`birth_term_time`、`timezone`。
- 天干/地支/藏干增加 `xun` 信息。
- `fetal_breath`（胎息）。
- `life_pillar`、`life_trigram`（命宫、命卦）。
- `shensha` 汇总列表。
- `day_master_strength`、`elements` 汇总信息。
- `calc_rules` 记录计算来源与规则说明。
- `target_flow` 使用传入的目标日期。
- `target_flow` 增加流月列表与目标年份小运。
- `relations`（目前仅天干合/冲、地支合/冲）。
- `start_date` 从 child limit 计算开始时间。
- 10 个大运统一输出结构。

## 计算逻辑调整

- `BirthChart` 增加 `minggong`、`minggua` 并输出到盘面。
- `minggong` 使用 tyme4py `get_own_sign`。
- `minggua` 使用八宅式计算方式（见 `calc_rules` 注释）。
- `taixi`（胎息）由日干 + 日支组合。
- 藏干条目补齐 `yinyang` 与 `xun`。
- 输出增加 `calc_rules` 与 `relations` 便于对照核验。
- 流月按十二节气起月（立春起寅月），小运沿用 tyme4py 的 child limit 逻辑。

## 神煞体系

- 用完整神煞体系替换旧的简化实现，规则来源于
  `cantian-tymext`（JS）并移植。
- 扩展 `src/divicast/entities/daemon.py` 的神煞枚举。
- `build_pillar_shensha` 统一按柱计算神煞，保持与参考实现一致。
- 当前仅实现一种流派；规则放在 `birth.py` 中，方便后续扩展。

## 测试与执行

- 单测改为传入目标日期以覆盖 `StandardBirthChartOutput`。
- 测试在 venv 中运行：`.venv/bin/python -m unittest`。

## 对照基准的已知差异

- 纳音名称差异（如“覆灯火/佛灯火”）。
- 戌藏干顺序在部分资料中不同（辛/丁顺序）。
- `relations` 仅实现合/冲，缺少刑/破/害/半合等。
- 个别日期的神煞仍有差异（需继续核对）。

## 准确性与完整性评价

- 核心柱信息（四柱、十神、藏干、纳音、空亡、长生）总体准确，和主流工具一致性高。
- 目前主要差异多为口径不同（纳音命名、藏干顺序、命卦算法、神煞规则）。
- `true_solar_birth`/`timezone` 未落地会影响时柱与起运等准确性。
- 盘面展示已基本齐全，适合“排盘展示 + 基础对照”。
- 专业盘面仍缺少关系体系扩展、流月/流日/流时、岁运并临、
  以及格局/用神/旺衰与调候等分析维度。

## 优先补齐项建议

- 关系体系：刑/害/破/半合/三合/六合/暗合/合化与化局判定。
- 真太阳时与时区：补齐 `true_solar_birth`/`timezone`，明确经度口径。
- 运势细化：流月/流日/流时、交运细则、岁运并临。
- 结构分析：格局、用神/喜忌、旺衰细化与调候。
- 神煞分层：本命/流年/流月/流日等层次区分与标注。

## 涉及文件

- `src/divicast/birth_chart/output.py`
- `src/divicast/birth_chart/birth.py`
- `src/divicast/entities/daemon.py`
- `tests/test_birth_chart.py`

---

## 格局计算模块 (2024)

### 新增文件

- `src/divicast/birth_chart/geju.py` - 格局计算模块
- `tests/test_geju.py` - 格局单元测试

### 格局枚举 (Geju)

共 44 种格局：

| 类别 | 数量 | 格局 |
|------|------|------|
| 正格 | 10种 | 正官、七杀、正财、偏财、正印、偏印、食神、伤官、比肩、劫财 |
| 从格 | 5种 | 从杀、从财、从儿、从印、从强 |
| 专旺格 | 5种 | 曲直、炎上、稼穑、润下、从革 |
| 化气格 | 10种 | 化甲、乙、丙、丁、戊、己、庚、辛、壬、癸 |
| 特殊格局 | 12种 | 魁罡、归禄、壬骑龙背、井栏叉、六甲趋干、六乙鼠贵、六阴朝阳、六壬趋艮、勾陈得位、玄武当权、两神成象、半壁江山 |

### 算法逻辑

1. **特殊格局**：优先判断（如魁罡格只需看日柱）
2. **专旺格**：某行占60%以上，日主无根且与最强五行一致
3. **化气格**：天干合化+化神占40%以上+日主无根
4. **从格**：日主无根+某行占60%以上
5. **正格**：月支藏干透出天干

### 待实现格局

- 禄刃格：建禄格、月刃格
- 日贵格：丁酉、丁亥、癸巳、癸卯日
- 日刃格：戊午、丙午、壬子日
- 日德格：甲寅、丙辰、戊辰、庚辰、壬戌日
- 金神格：时柱癸酉、己巳、乙丑
- 财官双美格：壬午、癸巳日
- 子午双包格：地支见两子或两午
