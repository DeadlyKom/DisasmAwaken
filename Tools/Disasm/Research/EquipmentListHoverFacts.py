"""Смысловое имя исходного JP наведения оснащения и договор его настоящего помощника."""
from PanelHoverFacts import CONTRACTS as HOVER_CONTRACTS
FUNCTIONS={0x7172:('HandleEquipmentListHover','JP-обёртка наведения оснащения с текущим счётчиком попыток рисователя')}
RENAMES={'HandleItem38':'HandleEquipmentListHover'}
LABELS={}
DOCUMENTS={('Station',0x7172):('EquipmentListPanels','непосредственное наведение, изменяемый RowCount и отсутствие дополнительного CPU-кадра')}
CONTRACTS={('Station',0x7172):tuple(list(part) for part in HOVER_CONTRACTS['Station',0x7210])}
CONTRACTS['Station',0x7172][3].append('JP передаёт тот же внешний CPU-возврат в UpdateEquipmentHover, нового кадра CALL нет')
COMMENTS={0x7172:(['передача наведения оснащения в UpdateEquipmentHover без дополнительного CPU-кадра'],None)}


def name_operands(region,address,operation):return operation
