from typing import List, Optional

from pydantic import BaseModel, Field
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from divicast.sixline.divinatory_symbol import DivinatorySymbol


class ShenSha(BaseModel):
    """神煞信息"""

    name: str = Field(description="神煞名称，如天乙贵人、驿马、桃花等")
    zhi: List[str] = Field(description="该神煞对应的地支列表")


class Fushen(BaseModel):
    """伏神信息"""

    relative: str = Field(description="伏神六亲（父母、兄弟、子孙、妻财、官鬼）")
    gan: str = Field(description="伏神的天干")
    zhi: str = Field(description="伏神的地支")
    wuxing: str = Field(description="伏神的五行属性")


class HexagramYao(BaseModel):
    """卦爻信息"""

    relative: str = Field(description="六亲（父母、兄弟、子孙、妻财、官鬼）")
    gan: str = Field(description="天干")
    zhi: str = Field(description="地支")
    wuxing: str = Field(description="五行属性（金、木、水、火、土）")
    line: str = Field(description="爻象（⚊阳爻，⚋阴爻）")
    is_subject: Optional[bool] = Field(None, description="是否为世爻")
    is_object: Optional[bool] = Field(None, description="是否为应爻")
    is_changed: Optional[bool] = Field(None, description="是否为动爻")
    fushen: Optional[Fushen] = Field(None, description="该爻下的伏神，若无伏神则为null")


class YaoDetail(BaseModel):
    """单爻详细信息"""

    liushen: str = Field(description="爻所临的六神（青龙、朱雀、勾陈、腾蛇、白虎、玄武）")
    origin: HexagramYao = Field(description="本卦爻的详细信息")
    variant: HexagramYao = Field(description="变卦爻的详细信息")


class StandardDivinatorySymbolOutput(BaseModel):
    """六爻排盘的完整结果"""

    yaogua: List[int] = Field(
        description="摇卦的原始记录数组，表示6次摇卦的结果，从初爻到上爻排列，对解卦无用处，仅供参考",
        json_schema_extra={
            "items": {
                "description": "单次摇卦的结果，3枚硬币中出现有字面的次数",
                "type": "integer",
                "enum": [0, 1, 2, 3],
            }
        }
    )
    time: str = Field(description="起卦的详细时间，格式：YYYY-MM-DD HH:MM:SS")
    bazi: str = Field(description="起卦时间的干支（四柱）")
    kongwang: str = Field(description="日柱对应的旬中空亡")
    guashen: str = Field(description="卦身")
    chuangzhang: List[str] = Field(description="床帐")
    xianggui: List[str] = Field(description="香闺")
    shensha: List[ShenSha] = Field(description="卦象中的神煞信息数组")
    benguaming: str = Field(description="本卦卦名")
    bianguaming: str = Field(description="变卦（之卦）的卦名")
    yao_1: YaoDetail = Field(description="初爻（最下爻）详细信息")
    yao_2: YaoDetail = Field(description="二爻详细信息")
    yao_3: YaoDetail = Field(description="三爻详细信息")
    yao_4: YaoDetail = Field(description="四爻详细信息")
    yao_5: YaoDetail = Field(description="五爻详细信息")
    yao_6: YaoDetail = Field(description="上爻（最上爻）详细信息")


def rich_draw_divination(ds: DivinatorySymbol):
    """
    接收一个 DivinatorySymbol 对象并使用 Rich 将其精美地打印到终端。
    """
    console = Console()

    # 1. 顶部信息区块
    coin_result_str = " ".join([cnt_to_str(c) for c in ds._cnts])

    info_text = Text()
    info_text.append("摇卦结果: ", style="bold")
    info_text.append(f"[{coin_result_str}]\n")

    daemon_str = " ".join(
        f"{d.chinese_name}-{''.join(str(z) for z in ds.daemons[d])}" for d in ds.daemons
    )
    guashen_str = f"{ds.guashen} 香闺-{''.join(str(z) for z in ds.xianggui)} 床帐-{''.join(str(z) for z in ds.chuangzhang)}"
    info_text.append("卦    身: ", style="bold")
    info_text.append(f"{guashen_str}\n")
    info_text.append("神    煞: ", style="bold")
    info_text.append(f"{daemon_str}\n")

    info_text.append("时    间: ", style="bold")
    info_text.append(f"{ds._time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    info_text.append("干    支: ", style="bold")
    info_text.append(f"{ds.bazi} ", style="bold green")
    info_text.append(
        f"(空亡: {ds.kongwang[0]}{ds.kongwang[1]})", style="bold red dim")

    info_panel = Panel(
        info_text,
        title="[bold cyan]摇卦信息[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )

    # 2. 本卦表格
    ben_gua_table = Table(
        title=f"[bold green] {ds.origin_hexagram.belongs_to_trigram()}:{ds.origin_hexagram.outside_trigram().primary_image}{ds.origin_hexagram.inside_trigram().primary_image}{ds.origin_hexagram}[/bold green]",
        border_style="green",
        header_style="bold green",
    )
    ben_gua_table.add_column("六神", justify="center", no_wrap=True)
    ben_gua_table.add_column("本卦", justify="center")
    ben_gua_table.add_column("爻", justify="center")
    ben_gua_table.add_column("标记", justify="left")

    # 3. 变卦表格
    bian_gua_table = Table(
        title=f"[bold magenta]变卦: {ds.variant_hexagram.outside_trigram().primary_image}{ds.variant_hexagram.inside_trigram().primary_image}{ds.variant_hexagram}[/bold magenta]",
        border_style="magenta",
        header_style="bold magenta",
    )
    bian_gua_table.add_column("变卦", justify="center")
    bian_gua_table.add_column("爻", justify="center")

    # 映射六神到颜色
    liushen_color_map = {
        "青龙": "[bright_green]青龙[/bright_green]",
        "朱雀": "[bright_red]朱雀[/bright_red]",
        "勾陈": "[yellow]勾陈[/yellow]",
        "腾蛇": "[dim black]腾蛇[/dim black]",
        "白虎": "[white]白虎[/white]",
        "玄武": "[blue]玄武[/blue]",
    }

    # 从上到下（六爻到初爻）填充表格
    for i in reversed(range(6)):
        line_pos = ds.lines[i]
        origin = line_pos.origin
        variant = line_pos.variant

        # --- 处理本卦列 ---
        liushen_cell = liushen_color_map.get(
            str(line_pos.liushen), str(line_pos.liushen))

        origin_info_text = Text(justify="left")
        origin_info_text.append(
            f"{origin.relative} {origin.gan}{origin.zhi}{origin.wuxing}"
        )
        if origin.fushen:
            fushen = origin.fushen
            origin_info_text.append(
                f"\n  (伏：{fushen.relative} {fushen.gan}{fushen.zhi}{fushen.wuxing})",
                style="dim",
            )

        origin_line_cell = "━━━" if origin.line.num == 1 else "━ ━"

        marker_text = Text("", justify="left")
        if line_pos.is_changed:
            marker_text.append("O " if origin.line.num ==
                               1 else "X ", style="bold red")
        else:
            marker_text.append("  ", style="dim")

        if origin.is_subject:
            marker_text.append("世", style="bold green")
        elif origin.is_object:
            marker_text.append("应", style="bold green")

        ben_gua_table.add_row(
            liushen_cell, origin_info_text, origin_line_cell, marker_text
        )

        # --- 处理变卦列 ---
        variant_info_cell = (
            f"{variant.relative} {variant.gan}{variant.zhi}{variant.wuxing}"
        )
        variant_line_cell = "━━━" if variant.line.num == 1 else "━ ━"

        # 如果本卦有伏神，变卦对应行需要加换行符来对齐
        if origin.fushen:
            variant_info_cell += "\n"
            variant_line_cell += "\n"

        bian_gua_table.add_row(variant_info_cell, variant_line_cell)

    # 4. 使用 Columns 并排显示
    gua_pan_columns = Columns([ben_gua_table, bian_gua_table], expand=False)

    # 5. 在终端中打印所有内容
    console.print("\n", info_panel, gua_pan_columns, "\n")


def plain_draw_divination(ds: DivinatorySymbol):
    """
    以纯文本形式返回六爻盘面内容的字符串表示。
    """

    z = (
        "摇卦结果: "
        + "[" + " ".join([cnt_to_str(cnt) for cnt in ds._cnts]) + "]\n"
    )
    a = "神煞: " + " ".join(
        f"{i}-{''.join(str(x) for x in ds.daemons[i])}" for i in ds.daemons
    )

    b = "时间: " + str(ds._time)
    c = "干支: " + str(ds.bazi) + \
        f" (空亡: {ds.kongwang[0]}{ds.kongwang[1]})"
    d = f"       {ds.origin_hexagram.belongs_to_trigram()}:{ds.origin_hexagram}                      {ds.variant_hexagram}"

    x = ""

    for i in reversed(range(6)):

        x = (
            x
            + str(ds.lines[i].liushen)
            + " "
            + str(ds.lines[i].origin.relative)
            + " "
            + f"{ds.lines[i].origin.gan}{ds.lines[i].origin.zhi}{ds.lines[i].origin.wuxing}"
            + " "
            + str(ds.lines[i].origin.line)
            + (
                "   "
                if not ds.lines[i].is_changed
                else " 〇" if ds.lines[i].origin.line.num == 1 else " × "
            )
            + (
                "世"
                if ds.lines[i].origin.is_subject
                else "应" if ds.lines[i].origin.is_object else "  "
            )
            + "     "
            + str(ds.lines[i].variant.relative)
            + " "
            + f"{ds.lines[i].variant.gan}{ds.lines[i].variant.zhi}{ds.lines[i].variant.wuxing}"
            + " "
            + str(ds.lines[i].variant.line)
            + (
                " "
                if ds.lines[i].origin.fushen is None
                else f"\n(伏：{ds.lines[i].origin.fushen.relative} {ds.lines[i].origin.fushen.gan}{ds.lines[i].origin.fushen.zhi}{ds.lines[i].origin.fushen.wuxing})"
            )
            + "\n"
        )

    return z + "\n" + a + "\n" + b + "\n" + c + "\n" + d + "\n" + x


def cnt_to_str(cnt: int) -> str:
    """
    将 cnt 转换为对应的字符串表示。
    """
    coin_map = {
        0: "(背)(背)(背)",
        1: "(字)(背)(背)",
        2: "(字)(字)(背)",
        3: "(字)(字)(字)",
    }
    return coin_map[cnt]


def to_standard_format(ds: DivinatorySymbol) -> StandardDivinatorySymbolOutput:
    """
    将 DivinatorySymbol 对象转换为标准Pydantic格式。
    """
    yao_objects = {}
    for i, data in enumerate(ds.lines, 1):
        yao_objects[f"yao_{i}"] = YaoDetail(
            liushen=str(data.liushen),
            origin=HexagramYao(
                relative=str(data.origin.relative),
                gan=str(data.origin.gan),
                zhi=str(data.origin.zhi),
                wuxing=str(data.origin.wuxing),
                line=str(data.origin.line),
                is_subject=data.origin.is_subject,
                is_object=data.origin.is_object,
                is_changed=data.is_changed,
                fushen=None if data.origin.fushen is None else Fushen(
                    relative=str(
                        data.origin.fushen.relative) if data.origin.fushen else None,
                    gan=str(
                        data.origin.fushen.gan) if data.origin.fushen else None,
                    zhi=str(
                        data.origin.fushen.zhi) if data.origin.fushen else None,
                    wuxing=str(
                        data.origin.fushen.wuxing) if data.origin.fushen else None
                )
            ),
            variant=HexagramYao(
                relative=str(data.variant.relative),
                gan=str(data.variant.gan),
                zhi=str(data.variant.zhi),
                wuxing=str(data.variant.wuxing),
                line=str(data.variant.line)
            )
        )
    sds = StandardDivinatorySymbolOutput(
        yaogua=ds._cnts,
        time=ds._time.strftime("%Y-%m-%d %H:%M:%S"),
        bazi=str(ds.bazi),
        kongwang=str(ds.kongwang[0]) + str(ds.kongwang[1]),
        guashen=str(ds.guashen),
        chuangzhang=[str(x) for x in ds.chuangzhang],
        xianggui=[str(x) for x in ds.xianggui],
        shensha=[ShenSha(name=str(x), zhi=[str(z) for z in y])
                 for x, y in ds.daemons.items()],

        benguaming=str(ds.origin_hexagram),
        bianguaming=str(ds.variant_hexagram),
        **yao_objects
    )
    return sds
