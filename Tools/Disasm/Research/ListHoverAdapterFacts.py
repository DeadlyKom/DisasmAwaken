"""Хвостовые обёртки наведения моделей, разделов справки и двух дисковых списков."""
from PanelHoverFacts import CONTRACTS as HOVER_CONTRACTS
ENTRIES=((0x6771,'HandleShipListHover','HandleItem25',0x67D0,'UpdateShipListHover','списка моделей кораблей'),
 (0x69DD,'HandleHelpIndexHover','HandleItem22',0x6A4B,'UpdateIndexListHover','разделов справки'),
 (0x741E,'HandleSaveSlotHover','HandleItem43',0x7482,'UpdateToPositionHover','позиций записи состояния'),
 (0x74A7,'HandleLoadSlotHover','HandleItem44',0x750B,'UpdateFromPositionHover','позиций чтения состояния'))
FUNCTIONS={a:(name,'Хвостовая передача наведения '+description+' в '+helper) for a,name,_,_,helper,description in ENTRIES}
RENAMES={old:name for _,name,old,_,_,_ in ENTRIES}
LABELS={}
DOCUMENTS={('Station',a):('ListHoverAdapters','тот же CPU-возврат, полный договор получателя и изменяемые счётчики строк') for a in FUNCTIONS}
CONTRACTS={};COMMENTS={}
for a,name,_,target,helper,description in ENTRIES:
 CONTRACTS['Station',a]=tuple(list(part) for part in HOVER_CONTRACTS['Station',target])
 CONTRACTS['Station',a][3].append('JP передаёт исходный внешний CPU-возврат в '+helper+', нового CALL и сохранённых слов нет')
 COMMENTS[a]=(['передача наведения '+description+' в '+helper+' с исходным адресом возврата'],None)


def name_operands(region,address,operation):return operation
