from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from divicast.entities.trigram import Hexagram
from divicast.time_utils import CalendarConvention
from divicast.sixline.casting import CastingInput, check_legacy_code
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
    is_changed: Optional[bool] = Field(None, description="是否为摇卦所得的明动爻；不表示日冲暗动，变卦同位不设置此值")
    fushen: Optional[Fushen] = Field(None, description="该爻下的伏神；无则为null，exclude_none序列化时省略")


class YaoDetail(BaseModel):
    """单爻详细信息"""

    liushen: str = Field(description="爻所临的六神（青龙、朱雀、勾陈、腾蛇、白虎、玄武）")
    origin: HexagramYao = Field(description="本卦爻的详细信息")
    variant: HexagramYao = Field(description="完整变卦同一爻位的信息；仅origin.is_changed为true时才是实际化出之爻")


class StandardDivinatorySymbolOutput(BaseModel):
    """六爻排盘的完整结果"""

    yaogua: List[Annotated[int, Field(strict=True, ge=0, le=3)]] = Field(
        min_length=6,
        max_length=6,
        description="旧版 divicast 编码，初爻到上爻：0老阴、1少阳、2少阴、3老阳；不是传统字面枚数",
    )
    # Optional when reading old JSON; new factory output always fills these fields.
    line_values: List[Literal[6, 7, 8, 9]] | None = Field(
        default=None, min_length=6, max_length=6, description="标准爻值，初爻到上爻：6老阴、7少阳、8少阴、9老阳"
    )
    casting: CastingInput | None = Field(default=None, description="输入口径与原始记录；旧JSON缺失时不推断来源")
    calendar: CalendarConvention | None = Field(default=None, description="本次实际采用的历法口径或显式四柱来源")
    time: str = Field(description="起卦的详细时间，格式：YYYY-MM-DD HH:MM:SS")
    bazi: str = Field(description="起卦时间的干支（四柱）")
    yuejian: str = Field(description="月建，月柱的地支")
    richen: str = Field(description="日辰, 日柱的地支")
    kongwang: str = Field(description="日柱对应的旬中空亡")
    guashen: str = Field(description="卦身")
    chuangzhang: List[str] = Field(description="床帐")
    xianggui: List[str] = Field(description="香闺")
    shensha: List[ShenSha] = Field(description="卦象中的神煞信息数组")
    benguaming: str = Field(description="本卦卦名")
    guagong: str = Field(description="本卦所属的卦宫")
    bengua_type: list[str] = Field(description="本卦的特殊类型")
    bianguaming: str = Field(description="变卦（之卦）的卦名")
    biangua_type: list[str] = Field(description="变卦的特殊类型")
    yao_1: YaoDetail = Field(description="初爻（最下爻）详细信息")
    yao_2: YaoDetail = Field(description="二爻详细信息")
    yao_3: YaoDetail = Field(description="三爻详细信息")
    yao_4: YaoDetail = Field(description="四爻详细信息")
    yao_5: YaoDetail = Field(description="五爻详细信息")
    yao_6: YaoDetail = Field(description="上爻（最上爻）详细信息")


def rich_draw_divination(ds: DivinatorySymbol) -> None:
    """
    接收一个 DivinatorySymbol 对象并使用 Rich 将其精美地打印到终端。
    """
    console = Console()

    # 1. 顶部信息区块
    coin_result_str = casting_to_str(ds)

    info_text = Text()
    info_text.append("起卦输入: ", style="bold")
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


def plain_draw_divination(ds: DivinatorySymbol) -> str:
    """
    以纯文本形式返回六爻盘面内容的字符串表示。
    """

    z = (
        "起卦输入: "
        + "[" + casting_to_str(ds) + "]\n"
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
    """Describe a legacy code without inventing physical coin provenance."""
    check_legacy_code(cnt)
    return f"{cnt}({('老阴', '少阳', '少阴', '老阳')[cnt]})"


def casting_to_str(ds: DivinatorySymbol) -> str:
    """Render recorded input semantics without guessing physical coin faces for legacy codes."""
    casting = ds.casting
    standard = " ".join(f"{value}({('老阴', '少阳', '少阴', '老阳')[value - 6]})" for value in ds.line_values)
    if casting.input_format == "legacy_yaogua":
        return "旧版编码: " + " ".join(cnt_to_str(value) for value in ds._cnts)
    if casting.input_format == "coin_counts":
        side = "字面" if casting.coin_side == "text" else "背面"
        return f"{side}枚数: " + " ".join(map(str, casting.values)) + "; 标准爻值: " + standard
    label = "模拟三枚硬币" if casting.input_format == "random_three_coins" else "标准爻值"
    return f"{label}: {standard}"


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
                    relative=str(data.origin.fushen.relative),
                    gan=str(data.origin.fushen.gan),
                    zhi=str(data.origin.fushen.zhi),
                    wuxing=str(data.origin.fushen.wuxing)
                )
            ),
            variant=HexagramYao(
                relative=str(data.variant.relative),
                gan=str(data.variant.gan),
                zhi=str(data.variant.zhi),
                wuxing=str(data.variant.wuxing),
                line=str(data.variant.line),
                is_subject=None, is_object=None, is_changed=None, fushen=None
            )
        )

    def hex_special_types(hex: Hexagram) -> list[str]:
        types = []
        if hex.is_liuhe():
            types.append("六合卦")
        if hex.is_liuchong():
            types.append("六冲卦")
        if hex.belongs_to_trigram_seq() == 7:
            types.append("游魂卦")
        if hex.belongs_to_trigram_seq() == 8:
            types.append("归魂卦")
        return types

    sds = StandardDivinatorySymbolOutput(
        yaogua=ds._cnts,
        line_values=ds.line_values,
        casting=ds.casting,
        calendar=ds.calendar,
        time=ds._time.strftime("%Y-%m-%d %H:%M:%S"),
        bazi=str(ds.bazi),
        yuejian=str(ds.bazi.month.zhi),
        richen=str(ds.bazi.day.zhi),

        kongwang=str(ds.kongwang[0]) + str(ds.kongwang[1]),
        guashen=str(ds.guashen),
        chuangzhang=[str(x) for x in ds.chuangzhang],
        xianggui=[str(x) for x in ds.xianggui],
        shensha=[ShenSha(name=str(x), zhi=[str(z) for z in y])
                 for x, y in ds.daemons.items()],

        benguaming=str(ds.origin_hexagram),
        guagong=str(ds.origin_hexagram.belongs_to_trigram()),
        bengua_type=hex_special_types(ds.origin_hexagram),
        bianguaming=str(ds.variant_hexagram),
        biangua_type=hex_special_types(ds.variant_hexagram),
        **yao_objects
    )
    return sds
