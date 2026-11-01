"""Один глиф либо физическая четырёхсимвольная клавишная подпись."""
import re
FIELDS=tuple(('Glyph'+str(i),1,'код символа позиции '+str(i+1)+' четырёхсимвольного обозначения') for i in range(4))
TABLE=('KeyAbbreviations','Source/Station/Data/KeyAbbreviations.asm',0x5E1B,0x5E27,'FKeyAbbreviation',FIELDS,('Enter','SymbolShift','Space'))
FUNCTIONS={0xBDF0:('DrawKeyLabel','Вывод одного глифа либо четырёх байтов обозначения Enter, Symbol Shift или Space')}
RENAMES={'UnknownBDF0':'DrawKeyLabel'}
LABELS={('Station',0xBDF8):'ExpandLabel'}
LABEL_RENAMES={'DrawKeyLabel.PointBDF8':'DrawKeyLabel.ExpandLabel'}
DOCUMENTS={('Station',0xBDF0):('KeyLabels','три физические записи, обёрнутое смещение и статус последнего из четырёх вызовов')}
CONTRACTS={('Station',0xBDF0):(
 ['AF содержит A полный код символа, F не является параметром',
  'TextWindow, шрифт, пиксельная часть и стек удовлетворяют DrawGlyph',
  'при A<21 доступны четыре байта от BE1B+((A-1E)*4 по модулю 256), штатные подписи задаются 1E..20'],
 ['HL, DE, BC сохранены, AF является результатом единственного либо последнего из четырёх DrawGlyph',
  "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
  'при A>=21 выполнен один DrawGlyph, при A<21 последовательно выполнены все четыре вызова',
  'курсор и bitmap содержат реально принятые глифы, CursorY не меняется'],
 ['AF, CursorX, bitmap и изменяемый GlyphState.DispatchTarget по договору DrawGlyph'],
 ['после отказа одного из четырёх глифов остальные вызовы всё равно выполняются, возвращается только последний статус',
  'для A<1E индекс заворачивается в байте и может читать соседние данные и код, диапазон трёх записей не проверяется',
  'внутренних переносов и завершения по CR/LF нет, все выбранные байты передаются непосредственно DrawGlyph'])}
COMMENTS={
 0xBDF0:(['проверка прямого глифа, порог 21 отделяет печатаемые коды от четырёхсимвольных обозначений'],None),
 0xBDF2:([],'переход, если входной код меньше 21, прочитать четыре байта обозначения'),
 0xBDF4:(['вывод единственного исходного глифа с возвратом его статуса'],None),
 0xBDF8:(['расчёт байтового смещения четырёхсимвольной записи, вычитание и умножение заворачиваются'],None),
 0xBDFC:(['сохранение указателей вызывающего кода на время обхода четырёх символов'],None),
 0xBE01:(['выбор исходной физической таблицы, отдельной проверки её границ нет'],None),
 0xBE05:(['вывод первого символа обозначения, промежуточные отказы не прерывают обход'],None),
 0xBE0A:(['вывод второго символа обозначения независимо от первого статуса'],None),
 0xBE0F:(['вывод третьего символа обозначения независимо от прежних статусов'],None),
 0xBE14:(['вывод четвёртого символа, только его AF возвращается вызывающему коду'],None)}
TARGETS={0xBDF8:'Station.DrawKeyLabel.ExpandLabel',0xAE8D:'Station.DrawGlyph.Entry',0xBE1B:'KeyAbbreviations.Enter'}


def name_operands(region,address,operation):
 if region!='Station' or address!=0xBDF0:return operation
 operation=operation.replace('@Station.UnknownBDF0.PointBDF8','@Station.DrawKeyLabel.ExpandLabel')
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 return operation.replace('CP #21','CP @KeyLabelConst.FirstDirect').replace('SUB #1E','SUB @KeyLabelConst.FirstExpanded')
