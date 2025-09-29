# 玄学排盘库

本库用于六爻排盘（六爻预测），提供了基础的六爻相关实体、符号、五行、天干地支等数据结构和推演逻辑，适合用于命理、易学、占卜等相关应用的开发。致力于面向未来，面向AI

## 功能简介

- 支持六爻排盘的基本流程
- 内置天干、地支、五行、六神、卦象等基础数据
- 提供六爻相关实体和符号的操作
- 易于扩展和集成到其他 Python 项目

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

如有问题或建议，欢迎提交 issue 或 PR
