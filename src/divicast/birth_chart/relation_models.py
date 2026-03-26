from __future__ import annotations

from ..base.symbol import ValuedMultiton
from ..entities.ganzhi import Dizhi, Tiangan
from ..entities.wuxing import Wuxing
from .analysis_enums import GanZhi, Zhu


class RelationType(ValuedMultiton):
    """关系的大类标签，用于输出中的 relation 字段。"""

    HE = (0, "合")
    CHONG = (1, "冲")
    XING = (2, "刑")
    HAI = (3, "害")
    PO = (4, "破")
    HUI = (5, "会")


class RelationPattern(ValuedMultiton):
    """具体关系模式。

    这里表示的是“哪一种关系规则”，例如天干五合、地支三刑。
    输出中的 `name` 直接来自这里，`relation` 则由它映射到 `RelationType`。
    """

    TIANGAN_CHONG = (0, "天干冲")
    TIANGAN_WU_HE = (1, "天干五合")
    DIZHI_XIANG_XING = (2, "地支相刑")
    DIZHI_LIU_CHONG = (3, "地支六冲")
    DIZHI_LIU_HE = (4, "地支六合")
    DIZHI_LIU_HAI = (5, "地支六害")
    DIZHI_LIU_PO = (6, "地支六破")
    DIZHI_SAN_HE = (7, "地支三合")
    DIZHI_SAN_HUI = (8, "地支三会")
    DIZHI_SAN_XING = (9, "地支三刑")
    DIZHI_ZI_XING = (10, "地支自刑")


class RelationQualifier(ValuedMultiton):
    """关系的细分说明，目前主要用于刑。"""

    WU_EN_ZHI_XING = (0, "无恩之刑")
    SHI_SHI_ZHI_XING = (1, "恃势之刑")
    WU_LI_ZHI_XING = (2, "无礼之刑")
    ZI_XING = (3, "自刑")


class RelationOutcomeKind(ValuedMultiton):
    """关系结果的表达方式。

    - `化`: 例如天干五合、地支六合中的“化土”
    - `局`: 例如地支三合、地支三会中的“火局”
    """

    HUA = (0, "化")
    JU = (1, "局")


RelationPattern._BELONGS_TO = {
    RelationType: {
        RelationPattern.TIANGAN_CHONG: RelationType.CHONG,
        RelationPattern.TIANGAN_WU_HE: RelationType.HE,
        RelationPattern.DIZHI_XIANG_XING: RelationType.XING,
        RelationPattern.DIZHI_LIU_CHONG: RelationType.CHONG,
        RelationPattern.DIZHI_LIU_HE: RelationType.HE,
        RelationPattern.DIZHI_LIU_HAI: RelationType.HAI,
        RelationPattern.DIZHI_LIU_PO: RelationType.PO,
        RelationPattern.DIZHI_SAN_HE: RelationType.HE,
        RelationPattern.DIZHI_SAN_HUI: RelationType.HUI,
        RelationPattern.DIZHI_SAN_XING: RelationType.XING,
        RelationPattern.DIZHI_ZI_XING: RelationType.XING,
    },
    GanZhi: {
        RelationPattern.TIANGAN_CHONG: GanZhi.TIANGAN,
        RelationPattern.TIANGAN_WU_HE: GanZhi.TIANGAN,
        RelationPattern.DIZHI_XIANG_XING: GanZhi.DIZHI,
        RelationPattern.DIZHI_LIU_CHONG: GanZhi.DIZHI,
        RelationPattern.DIZHI_LIU_HE: GanZhi.DIZHI,
        RelationPattern.DIZHI_LIU_HAI: GanZhi.DIZHI,
        RelationPattern.DIZHI_LIU_PO: GanZhi.DIZHI,
        RelationPattern.DIZHI_SAN_HE: GanZhi.DIZHI,
        RelationPattern.DIZHI_SAN_HUI: GanZhi.DIZHI,
        RelationPattern.DIZHI_SAN_XING: GanZhi.DIZHI,
        RelationPattern.DIZHI_ZI_XING: GanZhi.DIZHI,
    },
}


class RelationOutcome:
    """关系结果。

    目前只承载“化某五行”或“成某五行之局”两类结果，避免内部继续拼接字符串。
    """

    kind: RelationOutcomeKind
    wuxing: Wuxing

    def __init__(self, kind: RelationOutcomeKind, wuxing: Wuxing) -> None:
        self.kind = kind
        self.wuxing = wuxing

    def __str__(self) -> str:
        if self.kind == RelationOutcomeKind.HUA:
            return f"{self.kind}{self.wuxing}"
        return f"{self.wuxing}{self.kind}"


class RelationParticipant:
    """参与某条关系的具体柱位与干/支。"""

    pillar: Zhu
    position: GanZhi
    value: Tiangan | Dizhi

    def __init__(self, pillar: Zhu, position: GanZhi, value: Tiangan | Dizhi) -> None:
        self.pillar = pillar
        self.position = position
        self.value = value


class RelationPeer:
    """按柱索引视角下，除当前参与者外的其他参与方。"""

    pillar: Zhu
    value: Tiangan | Dizhi

    def __init__(self, pillar: Zhu, value: Tiangan | Dizhi) -> None:
        self.pillar = pillar
        self.value = value


class RelationEvent:
    """一条完整关系事件。

    `pattern` 是规则身份，输出层据此生成 `name` 和 `relation`；
    `qualifier` 与 `outcome` 只在少数关系中出现。
    """

    pattern: RelationPattern
    participants: list[RelationParticipant]
    outcome: RelationOutcome | None
    qualifier: RelationQualifier | None

    def __init__(
        self,
        pattern: RelationPattern,
        participants: list[RelationParticipant],
        outcome: RelationOutcome | None = None,
        qualifier: RelationQualifier | None = None,
    ) -> None:
        self.pattern = pattern
        self.participants = participants
        self.outcome = outcome
        self.qualifier = qualifier

    @property
    def name(self) -> str:
        return str(self.pattern)

    @property
    def relation_type(self) -> RelationType:
        return self.pattern.belongs_to(RelationType)


class RelationIndexEntry:
    """某柱某位置参与到的关系索引项。"""

    event_index: int
    pattern: RelationPattern
    peers: list[RelationPeer]
    outcome: RelationOutcome | None
    qualifier: RelationQualifier | None

    def __init__(
        self,
        event_index: int,
        pattern: RelationPattern,
        peers: list[RelationPeer],
        outcome: RelationOutcome | None = None,
        qualifier: RelationQualifier | None = None,
    ) -> None:
        self.event_index = event_index
        self.pattern = pattern
        self.peers = peers
        self.outcome = outcome
        self.qualifier = qualifier

    @property
    def name(self) -> str:
        return str(self.pattern)

    @property
    def relation_type(self) -> RelationType:
        return self.pattern.belongs_to(RelationType)


class PillarRelationIndex:
    """单柱索引视角下的天干/地支关系列表。"""

    tiangan: list[RelationIndexEntry]
    dizhi: list[RelationIndexEntry]

    def __init__(self) -> None:
        self.tiangan = []
        self.dizhi = []

    def for_position(self, position: GanZhi) -> list[RelationIndexEntry]:
        if position == GanZhi.TIANGAN:
            return self.tiangan
        return self.dizhi


class RelationIndexByPillar:
    """按柱位组织的关系索引。"""

    year: PillarRelationIndex
    month: PillarRelationIndex
    day: PillarRelationIndex
    hour: PillarRelationIndex
    _index_by_zhu: dict[Zhu, PillarRelationIndex]

    def __init__(self) -> None:
        self.year = PillarRelationIndex()
        self.month = PillarRelationIndex()
        self.day = PillarRelationIndex()
        self.hour = PillarRelationIndex()
        self._index_by_zhu = {
            Zhu.YEAR: self.year,
            Zhu.MONTH: self.month,
            Zhu.DAY: self.day,
            Zhu.HOUR: self.hour,
        }

    def for_pillar(self, pillar: Zhu) -> PillarRelationIndex:
        return self._index_by_zhu[pillar]


class RelationAnalysis:
    """关系事件列表以及按柱位回查索引。"""

    events: list[RelationEvent]
    pillar_index: RelationIndexByPillar

    def __init__(self) -> None:
        self.events = []
        self.pillar_index = RelationIndexByPillar()

    def add_event(self, event: RelationEvent) -> None:
        event_index = len(self.events)
        self.events.append(event)

        for participant in event.participants:
            bucket = self.pillar_index.for_pillar(participant.pillar)
            peers = [
                RelationPeer(pillar=other.pillar, value=other.value)
                for other in event.participants
                if other is not participant
            ]
            bucket.for_position(participant.position).append(
                RelationIndexEntry(
                    event_index=event_index,
                    pattern=event.pattern,
                    peers=peers,
                    outcome=event.outcome,
                    qualifier=event.qualifier,
                )
            )
