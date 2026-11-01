"""Действие карты системы, ближайший вариант настоящей сцены и условное снятие периодической цели."""
import re
FUNCTIONS={0x783B:('HandleSystemMapAction','Выбор ближайшего варианта системы либо закрытие карты с отключением её периодического обновления')}
RENAMES={'Unknown783B':'HandleSystemMapAction'}
LABELS={('Station',0x784E):'CloseResult',('Station',0x784F):'SelectVariant'}
LABEL_RENAMES={'HandleSystemMapAction.Point784E':'HandleSystemMapAction.CloseResult','HandleSystemMapAction.Point784F':'HandleSystemMapAction.SelectVariant'}
DOCUMENTS={('Station',0x783B):('SystemMapAction','реальные курсоры сцены, точный нулевой выход, координатные переносы и периодическая цель')}
CONTRACTS={('Station',0x783B):(
 ['HL запасной рисователь карты, DE индекс элемента 20, BC контекст, AF полный селектор, IX выбранная FInterfaceItem',
  'действуют договоры RepaintAndFlag и CloseMenuOnRow, банк станции 0 выбран, исходный список и хвосты сдвига доступны',
  'для селектора 1 MapSelection содержит выбранный пятибайтовый ключ, KARTA загружена в банк 1, переключение страниц разрешено',
  'VariantPanelState.ItemIndex задаёт читаемые X и Y панели, Cursor0..Cursor5 банка 1 соответствуют текущим точкам сцены',
  'действуют договоры DescribeKeyBanked, SelectNearestMapVariant, BeginScreenUpdate, условных панелей и EndScreenUpdate, HALT корректно пробуждается'],
 ['при Carry общего обработчика сразу возвращён его результат, последующие ветви выбора и закрытия не исполняются',
  'для селектора не 1 после разрешённого общего пути выполнен CloseMenuOnRow, при его Z=1 HL=EmptyCallback и PeriodicCall заменён на этот адрес',
  'при Z=0 CloseMenuOnRow его результаты возвращены без самостоятельной записи PeriodicCall',
  'для селектора 1 количество N=max(((XOR четырёх выбранных байтов) AND 7)-1,0), при N=0 немедленно возвращён результат DescribeKeyBanked',
  "нулевой путь возвращает HL и DE характеристики ключа, BC сохранён от входа DescribeKeyBanked, AF=0044 либо 0042, AF' содержит страницу возврата и её OR-флаги",
  'при N=1..6 MapSelection.Variant содержит индекс первого ближайшего из N текущих курсоров, Origin собран из физических X и Y панели',
  'после выбора последовательно вызваны BeginScreenUpdate, TryDrawSystemInfo и TryDrawVariantPanel, затем EndScreenUpdate',
  'после экранного цикла HL, DE, BC и альтернативные общие пары соответствуют выполненным панелям, A=10 и F сохранён от последнего рисователя либо его проверки',
  'при экранном цикле CurrentPage=10, указатель возобновлён, UpdateBlocked=0, PeriodicCall определяется последним DrawVariantPanel при его присутствии',
  'IY, I, IFF и IM сохранены при договоре IRQ, IX может измениться подготовкой ресурсов панели, SP обычного возврата входному+2'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX по подготовке ресурсов, MapSelection.Variant, Minimum, рабочий ключ, список, callback, экраны и текстовое состояние"],
 ['нулевая ветвь сама не меняет номер варианта и периодическую цель, предшествующие эффекты RepaintAndFlag этим не отменяются',
  'Origin является целым упакованным словом, Target=PointerWord-(8×((Origin+0404) AND FFFF)+0603) по модулю 65536, переносы между X и Y не разделяются',
  'при равных квадратах расстояний прежний индекс остаётся, принудительной замены последним совпадением нет',
  'отключение PeriodicCall относится к Z результата CloseMenuOnRow, оно не выполняется просто от любого неселективного A',
  'собственный переход SelectVariant по 784F обходит общий префикс, номер вариантов и ресурсы обязаны быть подготовлены вызывающим окружением',
  'модель использует настоящие ресурсные координаты после DrawVariantPanel, независимый oracle всего повторного bitmap не заявлен'])}
COMMENTS={0x783B:(['обновление общей геометрии и порядка карты перед разбором селектора'],None),0x783E:([],'выход, если общий обработчик вернул Carry, выбор и закрытие не разрешены'),
 0x783F:(['проверка селектора 1 для выбора варианта'],None),0x7840:([],'переход, если селектор равен 1, вычислить ближайший вариант'),
 0x7843:(['удаление карты только при совпадении символьных строк указателя и начала окна'],None),0x7846:([],'переход, если символьные строки различаются, периодическую цель самостоятельно не менять'),
 0x7848:(['обновление периодической цели пустым RET после разрешённого закрытия'],None),
 0x784F:(['чтение полного выбранного ключа для количества вариантов и его характеристики'],None),0x785C:([],'выход, если количество вариантов равно нулю, ближайший вариант не вычислять'),
 0x785D:(['сохранение ненулевого количества в AF на время чтения координат панели через альтернативный набор'],None),
 0x785E:(['поиск физических FInterfaceItem.X и Y текущей панели вариантов'],None),0x7865:(['создание упакованного Origin, младший X и старший Y, это не пиксельное начало текстового окна'],None),
 0x7869:(['выбор банка KARTA с сохранением экранного бита'],None),0x786E:(['восстановление количества и поиск первого ближайшего из текущих курсоров'],None),
 0x7872:(['возврат банка станции после записи нового MapSelection.Variant'],None),0x7877:(['создание теневого снимка перед последовательным обновлением двух зависимых панелей'],None),
 0x787A:(['обновление информации о выбранной системе только при точном присутствии её рисователя'],None),0x787D:(['обновление карты и её ресурсов только при точном присутствии рисователя'],None),
 0x7880:(['показ обновлённого базового экрана и возобновление указателя'],None)}
TARGETS={0xCBEB:'Station.RepaintAndFlag.Entry',0xC85E:'Station.CloseMenuOnRow.Entry',0x9A58:'Station.EmptyCallback.Entry',0x9A89:'MenuCommandState.PeriodicCall',
 0x9848:'MapSelection.Variant',0x9844:'MapSelection.FirstWord',0x9846:'MapSelection.SecondWord',0xA46E:'Station.DescribeKeyBanked.Entry',
 0x788D:'VariantPanelState.ItemIndex',0x9EED:'Station.GetItemField.Entry',0x6396:'Station.SelectRamBank.Entry',0xC5E8:'Map.SelectNearestMapVariant.Entry',
 0xA49F:'Station.BeginScreenUpdate.Entry',0x7688:'Station.TryDrawSystemInfo.Entry',0x7885:'Station.TryDrawVariantPanel.Entry',0xA496:'Station.EndScreenUpdate.Entry',
 0x784E:'Station.HandleSystemMapAction.CloseResult',0x784F:'Station.HandleSystemMapAction.SelectVariant'}
MODIFIED_WRITES=((0x784B,0x9A89,'Station',0x9A88,2,2),)


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 for old,new in LABEL_RENAMES.items():operation=operation.replace('@Station.'+old,'@Station.'+new)
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 return operation.replace('LD A, #11','LD A, @SystemNameConst.MapPage').replace('LD A, #10','LD A, @StationIrqConst.StationPage')
