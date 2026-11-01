"""Индексатор HELP банка 7, физическая таблица и предусловия исходного LDIR."""
FIELDS=(('TextAddress',2,'рабочий адрес начала строки, ноль после последней заполненной записи'),)
TABLE=('HelpLineCache','Source/Help/Data/LinePointers.asm',0x7C,0x87C,'FHelpLinePointer',FIELDS,tuple('Line'+str(i).zfill(4) for i in range(1024)))
FUNCTIONS={0xDB00:('IndexTextLines','Индексирование выбранной LF-записи по правилам переноса строк и обнуление остатка таблицы')}
CONTRACTS={('Help',0xDB00):(
 ['HELP загружен в банк 7, выбран через порт 7FFD, текст Station и таблица ширин доступны',
  'HelpTextState.RecordOperand задаёт пропуск A+1 байтов LF от E3E2, все читаемые байты существуют',
  'TextWindow содержит геометрию, каждый SkipJustifyRow продвигает HL либо возвращает Carry',
  'число получаемых строк N находится в пределах 1..1023, стек доступен и не пересекает рабочие области'],
 ['HL равен E37B, DE содержит N включая последнюю строку, BC равен нулю',
  'AF содержит A=68 при Height>=14, иначе A=Height, F=(A&02)*16|(A&08)',
  "HL', DE', BC', AF', IY, I, IFF и IM сохранены, IX указывает за N заполненными словами",
  'первые N записей HelpLineCache содержат начала строк, оставшиеся слова обнулены',
  'SP после RET равен входному+2, страница не переключается, bitmap не меняется'],
 ['HL, DE, BC, AF, IX, HelpLineCache, TextWindow.CursorX, TextWindow.CursorY',
  'изменяемые операнды и служебный префикс SkipJustifyRow, после прохода префикс равен 68, 48, 26'],
 ['при N=1024 исходный DEC BC даёт FFFF перед LDIR, ограничение не исправлено',
  'проверка продвижения и ёмкости отсутствует, неподходящая геометрия может зациклить обход',
  'договор проверен на исходных инструкциях моделью, без ассемблирования, IRQ и нативного запуска'])}
DOCUMENTS={('Help',0xDB00):('HelpLineIndex','таблица строк, независимая раскладка и предел исходного LDIR')}


def name_operands(region,address,operation):
 if region!='Help' or address!=0xDB00:return operation
 for old,new in (('#A390','@Station.SkipLfRecords.Entry'),('#AD35','@Station.SkipJustifyRow.Entry'),
  ('(#6320)','(@TextWindow.CursorX)'),('(#6321)','(@TextWindow.CursorY)'),('#DB7C','@HelpLineCache.Line0000'),
  ('#0400','@HelpLineConst.Capacity'),('(IX + #00)','(IX + @FHelpLinePointer.TextAddress)'),
  ('(IX + #01)','(IX + @FHelpLinePointer.TextAddress + 1)'),('@Help.IndexTextLines.PointDB13','@Help.IndexTextLines.StoreLine')):
  operation=operation.replace(old,new)
 return operation
