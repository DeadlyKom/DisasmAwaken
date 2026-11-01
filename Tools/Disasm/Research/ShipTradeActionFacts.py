"""Подтверждение текущей модели, реальный LANG и безусловное завершение панелей после его возврата."""
import re
FUNCTIONS={0x79C7:('ConfirmShipModelTrade','Передача выбранной модели событию LANG и закрытие списка с пятью связанными панелями')}
RENAMES={'Unknown79C7':'ConfirmShipModelTrade'}
LABELS={('Station',0x79E4):'SelectCategory',('Station',0x79ED):'RunEvent'}
LABEL_RENAMES={'ConfirmShipModelTrade.Point79E4':'ConfirmShipModelTrade.SelectCategory','ConfirmShipModelTrade.Point79ED':'ConfirmShipModelTrade.RunEvent'}
DOCUMENTS={('Station',0x79C7):('ShipTrade','события 1..4, фактический сценарий, ранний FF и завершение интерфейса')}
CONTRACTS={('Station',0x79C7):(
 ['HL, DE, BC и AF не задают действие, строка берётся из PanelHoverState.ShipsRow',
  'банк станции 0 выбран, D3D находится в банке 4, LANG в банке 6, переключение страниц не заблокировано',
  'строка FF означает отсутствие выбора, иначе сумма строки с D3DPreviewState.BaseOperand должна задавать доступную запись сценария',
  'действуют договоры RunMarketScript, BeginScreenUpdate, DrawItem00, EndScreenUpdate и удаления рисователей',
  'поля состояния игрока и модели, исходные таблицы и тексты подготовлены, шесть изменяемых индексов доступны'],
 ['при ShipsRow=FF немедленный RET, A=0,F=50 OR входной Carry, остальные пары, память, банки, I и IFF сохранены',
  'иначе байт строки записан в D3DPreviewState.RowOperand банка 4, BaseOperand не меняется этим обработчиком',
  'EventCode=1+(OwnedMode<>0)+2*(Selector<>0), для любого ненулевого полного байта используется соответствующая единица',
  'в банке LANG 6 исполняется исходный RunMarketScript, эффекты сделки и очереди сообщения определяются его условиями',
  'после нормального возврата LANG последовательно выполнены BeginScreenUpdate, DrawItem00 и EndScreenUpdate',
  'удалены первые совпадения индекса списка моделей и пяти индексов DropShipDetailPanels, даже при отказе сценария',
  'HL=EmptyCallback, DE=последний индекс Index29, BC и альтернативные общие пары соответствуют выходу LANG и DrawItem00',
  'AF=0044, AF\' по экранному циклу, IX по выходу LANG, IY, I, IFF и IM сохранены при договорах вызываемых процедур',
  'ActiveItemState.Active=0, PeriodicCall=EmptyCallback, CurrentPage=10 и указатель возобновлён, SP после RET входному+2'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX по LANG, состояние игрока по событию, строка D3D, экран, список и операнды помощников"],
 ['ранний FF не вычисляет событие и не выбирает банк, сохранение Carry относится только к нему',
  'события 3 и 4 не имеют соответствующих блоков в активном исходном сценарии, общий начальный T всё равно пересчитывает загрузку',
  'отказ сделки через M не отменяет последующее закрытие панелей вызывающим обработчиком',
  'сдвиг каждого найденного ключа переносит физические 128 байтов, включая хвост после ограничителя списка',
  'модель исполняет исходные LANG и статусный рисунок, независимое сравнение всего bitmap статуса и нативный запуск здесь не заявлены'])}
COMMENTS={0x79C7:(['чтение строки подтверждаемой модели независимо от входного селектора A'],None),
 0x79CA:(['проверка отсутствия наведения по переполнению FF в ноль'],None),0x79CB:([],'выход, если строка равна FF, модель и банки не менять'),
 0x79CC:(['выбор банка D3D для обновления исходного операнда строки'],None),
 0x79D4:(['обновление компонента строки, смещение списка BaseOperand сохраняется'],None),
 0x79D7:(['возврат банка станции перед чтением режимов интерфейса'],None),
 0x79DC:(['чтение изменяемого полного режима покупки либо продажи'],None),0x79DE:(['проверка нулевого режима покупки'],None),
 0x79E1:([],'переход, если OwnedMode равен нулю, оставить событие покупки 1'),0x79E3:(['расчёт события продажи 2 для ненулевого режима'],None),
 0x79E7:(['проверка полного селектора категории модели'],None),0x79E9:([],'переход, если Selector равен нулю, оставить корабельное событие 1 либо 2'),
 0x79EB:(['расчёт события второй категории добавлением двух по модулю 256'],None),
 0x79ED:(['обновление события перед входом в исходный LANG'],None),0x79F0:(['выбор банка LANG, исходные события 3 и 4 отдельных ветвей не имеют'],None),
 0x79F5:(['выполнение исходного сценария, отказ сделки не отменяет следующие действия интерфейса'],None),
 0x79F8:(['возврат банка станции после нормального выхода интерпретатора'],None),
 0x79FD:(['создание снимка экрана перед обновлением статуса игрока'],None),
 0x7A03:(['показ обновлённого статуса с возобновлением указателя'],None),
 0x7A06:(['чтение изменяемого индекса списка моделей для удаления'],None),
 0x7A0A:(['удаление списка моделей независимо от результата сделки'],None),
 0x7A0D:(['удаление пяти связанных панелей с отключением периодического просмотра'],None),
 0x7A10:(['обновление активности в ноль после завершения группы'],None)}
TARGETS={0x67D7:'PanelHoverState.ShipsRow',0x6396:'Station.SelectRamBank.Entry',0xE146:'D3DPreviewState.RowOperand',
 0x6906:'ShipPanelState.Selector',0x983A:'ScriptCallState.EventCode',0xC000:'Text.RunMarketScript.Entry',
 0xA49F:'Station.BeginScreenUpdate.Entry',0x7F35:'Station.DrawItem00.Entry',0xA496:'Station.EndScreenUpdate.Entry',
 0x67E1:'ModelListState.ItemIndex',0xC873:'Station.DropItemDraw.Entry',0x6780:'Station.DropShipDetailPanels.Entry',
 0x9E78:'ActiveItemState.Active',0x79E4:'Station.ConfirmShipModelTrade.SelectCategory',0x79ED:'Station.ConfirmShipModelTrade.RunEvent'}
MODIFIED_WRITES=((0x79D4,0xE146,'D3D',0xE145,1,4),)


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
