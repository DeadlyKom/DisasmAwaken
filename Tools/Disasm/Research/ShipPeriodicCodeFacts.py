"""Доказанная достижимость корабельных периодических входов, полные договоры пока Unknown."""
DOCUMENTS={('Station',a):('ShipPeriodicCode','условные продолжения и границы разбора корабельного callback') for a in (0x6870,0x68CC,0x68EA,0x693E)}
COMMENTS={0x6876:([],'выход, если точного рисователя DrawItem26 нет в текущем списке'),
 0x6944:([],'выход, если точного рисователя DrawModelDescriptionPanel нет в текущем списке'),
 0x68D0:([],'выход, если ActiveItemState.Active ненулевой, отложить обновление'),
 0x68ED:([],'переход, если PendingRedraw ненулевой, обработать отложенное обновление'),
 0x68F8:([],'выход, если последний рисователь не равен DrawItem26.Entry')}


def name_operands(region,address,operation):
 if region!='Station':return operation
 if address in (0x6870,0x68EA):operation=operation.replace('LD DE, #6877','LD DE, @Station.DrawItem26.Entry')
 if address==0x693E:operation=operation.replace('LD DE, #6945','LD DE, @Station.DrawModelDescriptionPanel.Entry')
 if address==0x6877:operation=operation.replace('LD HL, #68EA','LD HL, @Station.Unknown68EA.Entry')
 return operation

from ShipPreviewCallbackFacts import COMMENTS as PREVIEW_COMMENTS
COMMENTS.update(PREVIEW_COMMENTS)
