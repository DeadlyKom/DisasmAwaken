"""Список CR-заголовков и окно LF-текста справки, исходные рисователи 22 и 23."""
import re
FUNCTIONS={0x69A8:('DrawHelpText','Рамка панели справки, повторное индексирование выбранной записи и печать от TopLine'),
 0x6A5B:('DrawHelpContents','Рамка списка разделов справки, сброс подсветки и пересчёт числа видимых CR-заголовков')}
RENAMES={'DrawItem23':'DrawHelpText','DrawItem22':'DrawHelpContents'}
LABELS={('Station',0x6A6C):'RenderTitles'}
DOCUMENTS={('Station',a):('HelpPanels','рамки, действующие HELP-вызовы, прокрутка и байтовый предел наведения') for a in FUNCTIONS}
CONTRACTS={('Station',0x69A8):(
 ['Entry с кодом LD HL требует HelpPanelState.TextIndex как индекс подготовленного FInterfaceItem, штатно 23',
  'геометрия и Flags удовлетворяют DrawCaptionItem, действуют его договор рамки, шрифта и пробуждения HALT',
  'HelpPanelState.TopLine содержит допустимый индекс таблицы, HELP подготовлен и выполняется договор IndexHelpText',
  'страница 10 либо 18 согласована с портом, IRQ сохраняет контекст и данные изменяемых писателей'],
 ['при исходном LD HL сначала DrawCaptionItem рисует рамку, затем IndexHelpText обновляет всю таблицу и LineCount',
  'HL, DE, BC, AF являются результатом PrintHelpLine для TopLine, AF=1000 либо 180C',
  "HL', DE', BC', IY сохранены, AF' рабочий в рамке, IX=DB7C+2*N",
  'Style=1, курсор и bitmap содержат результат рамки и печати, TopLine не меняется',
  'банк 0 и исходный экранный бит восстановлены, SP после RET равен входному+2',
  'при временном C9 в Entry сохраняются все регистры, флаги и память, SP после RET входному+2'],
 ["HL, DE, BC, AF, AF', IX, таблица HELP, LineCount, курсор, окно, bitmap и изменяемые операнды помощников"],
 ['код не выходит после неудачи заголовка, выполняются последующие индексирование и печать',
  'нулевая запись TopLine подавляет только вывод текста, рамка и повторное индексирование уже выполнены',
  'модель охватывает девять исходных записей, два значения TopLine, три геометрии и оба экранных бита']),
 ('Station',0x6A5B):(
 ['Entry с кодом LD HL требует HelpPanelState.ContentsIndex как индекс FInterfaceItem, штатно 22',
  'геометрия, Flags, шрифт, стек и IRQ удовлетворяют DrawCaptionItem',
  'HelpPanelState.ContentsTop содержит L номер существующего CR-заголовка, его H сохраняется в DE при печати',
  'HELP загружен в банк 7, страница 10 либо 18 согласована с портом, переключения не заблокированы'],
 ['HL указывает на остановку PrintCrRecordAndRows, DE равен входному ContentsTop, BC сохранён',
  'AF содержит число строк и флаги формулы PrintCrRecordAndRows, AF\' равен 1000 либо 180C',
  "HL', DE', BC', IX и IY сохранены, I, IFF и IM сохраняются при договоре IRQ",
  'IndexRow=FF, Style=0, VisibleTitles получает полный байтовый результат числа строк',
  'CursorY=8, CursorX после печати, bitmap содержит рамку и оставшиеся заголовки от ContentsTop',
  'банк 0 и экранный бит восстановлены, SP после RET входному+2',
  'при временном C9 в Entry сохраняются все регистры, флаги и память, SP после RET входному+2'],
 ["HL, DE, AF, AF', IndexRow, VisibleTitles, курсор, окно, bitmap и изменяемые операнды помощников"],
 ['VisibleTitles является операндом D в UpdateIndexListHover, он ограничивает область вычисления строки',
  'между CR-заголовками нет LF, печатается остаток потока до общего LF либо отказа окна',
  'число строк берётся из AF\' печатателя после возврата банка, не из его основного A=8'])}
COMMENTS={
 0x69A8:(['чтение изменяемого индекса панели справки, назначаемого исходным интерфейсом'],None),
 0x69AB:(['создание рамки и заголовка, подготовка геометрии содержимого'],None),
 0x69AE:(['обновление всей таблицы визуальных строк текущей LF-записи'],None),
 0x69B1:(['чтение полного индекса верхней строки для текущей прокрутки'],None),
 0x69B4:(['печать от выбранного указателя, нулевая запись не выводит содержимого'],None),
 0x6A5B:(['чтение изменяемого индекса панели списка разделов'],None),
 0x6A5E:(['рисование рамки и заголовка до изменения состояния подсветки'],None),
 0x6A61:(['сброс прежней XOR-полосы, фон уже заменён рамкой и содержимым'],None),
 0x6A66:(['отключение переноса остатка заголовка при отказе ширины'],None),
 0x6A69:(['чтение верхнего CR-заголовка списка, младший байт выбирает запись'],None),
 0x6A6C:(['выбор банка HELP с сохранением экранного бита'],None),
 0x6A71:(['печать CR-потока и расчёт числа строк в альтернативном AF'],None),
 0x6A74:(['возврат банка станции перед чтением альтернативного результата'],None),
 0x6A79:(['получение числа строк, AF переключателя сохраняется в альтернативном наборе'],None),
 0x6A7A:(['обновление байтового предела строк в исходном LD DE обработчика наведения'],None)}
TARGETS={0xC287:'Station.DrawCaptionItem.Entry',0x69B8:'Station.IndexHelpText.Entry',0x699D:'HelpPanelState.TopLine',0x69CF:'Station.PrintHelpLine.Entry',
 0x6A52:'PanelHoverState.IndexRow',0x6A7E:'Station.DisableTextWrap.Entry',0x6A15:'HelpPanelState.ContentsTop',0x6396:'Station.SelectRamBank.Entry',
 0xDB5B:'Help.PrintCrRecordAndRows.Entry',0x6A4D:'HelpPanelState.VisibleTitles'}
MODIFIED_WRITES=((0x6A63,0x6A52,'Station',0x6A51,1,5),(0x6A7A,0x6A4D,'Station',0x6A4B,1,5))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
