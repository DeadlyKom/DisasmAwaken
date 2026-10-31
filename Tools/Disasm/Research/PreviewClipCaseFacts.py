"""Фактические табличные обработчики D3D, совпадение структуры предварительно проверено побайтно."""
import re
from ClipCaseFacts import LABELS as CASE_LABELS, COMMENTS as CASE_COMMENTS
from MapClipCasesFacts import LABELS as TAIL_LABELS
FUNCTIONS={0xE1EB:('PreviewClipCases','Решения отсечения по паре зон, порядок пересечений и накопление отметок углов')}
ENDS={0xE1EB:0xE5E8}
LABELS={('D3D',a+0xD06):name for (region,a),name in {**CASE_LABELS,**TAIL_LABELS}.items() if region=='Map' and 0xD4E5<a<0xD8E2}
INTERNAL_ROOTS=tuple(a for region,a in LABELS)
DOCUMENTS={('D3D',0xE1EB):('PreviewClipCases','81 пара зон, 241 явный путь, готовность кэшей, отметки углов и два вида внешнего кадра')}
COMMENTS={a+0xD06:(before.copy(),right) for a,(before,right) in CASE_COMMENTS.items() if 0xD4E5<=a<0xD8E2}
COMMENTS[0xE1EB]=(['пустой табличный обработчик, переход к возврату, установленному внешним диспетчером'],None)
for a,(before,right) in list(COMMENTS.items()):
 def coordinates(text):return text.replace('X2 минус X1','колонки второго конца минус колонка первого').replace('Y2 минус Y1','строки второго конца минус строка первого')
 COMMENTS[a]=([coordinates(v) for v in before],coordinates(right) if right else None)
CONTRACTS={('D3D',0xE1EB):(
 ['HL, DE, BC и AF рабочий входной контекст выбранного обработчика, координаты читаются из физических записей',
  "HL', DE', BC' сохраняются, AF' и IX используются вложенной арифметикой, IY сохраняется",
  'PreviewClipFirst и PreviewClipSecond содержат слова колонок и строк с соответствующими кодами сторон',
  'SeenFlags содержит прежние отметки, BlockCode=0 разрешает запись углов, любой ненуль подавляет её',
  'ByteCount и страница C8 доступны, каждый делитель имеет ненулевой знаменатель и допустимое слово частного',
  'EAB6 устанавливает три возврата EB08, E171 устанавливает E1E2 над сохранёнными BC и HL',
  'внутренние продолжения требуют уже готовые кэши, входить в них без предшествующего пути нельзя'],
 ['HL, DE, BC и AF обычного RET равны контексту последнего действия пути, BIT и SET учитываются после него',
  "HL', DE', BC' сохранены, AF' и IX определяются исполненными умножениями и делениями, IY сохранён",
  'порядок добавлений, конкретные условия и отметки каждого входа перечислены в PreviewClipCaseDecisions',
  'SeenFlags меняет только младшие четыре бита установкой отметок, старшая тетрада сохраняется',
  'при BlockCode!=0 путь добавляет не более двух точек, при BlockCode=0 в проверенной области не более четырёх',
  'обычный RET снимает одно слово, окончательные регистры и SP определяются внешним кадром',
  'специальный выход UnwindPreviewClipFrame снимает три слова, для трёх EB08 даёт HL=EBF2, BC=00EA, AF=EBA9',
  'I, IFF и IM сохраняются, физические записи концов и BlockCode эта группа не изменяет'],
 ["HL, DE, BC, AF, AF', IX по исполненному пути, SeenFlags, выбранные кэши, ByteCount, выходные точки и CPU-стек"],
 ['Entry состоит из RET и не является общим эпилогом, оба эпилога принадлежат внешним диспетчерам',
  'разность двух 32-битных произведений выбирает порядок пересечений по биту 31, равенство входит в неотрицательную ветвь',
  'BIT читает прежнюю отметку, SET её устанавливает без изменения флагов, поэтому последующий CALL NZ проверяет прежний BIT',
  'отметить угол и добавить угол разные действия, BlockCode подавляет только запись углового помощника',
  'все 71 физическая цель и 241 путь проверены, готовность кэшей установлена для обеих ветвей каждого условия',
  '178612 исполнений охватывают шесть нулевых минимумов, все начальные SeenFlags и оба режима BlockCode',
  'полный символьный конечный контекст каждого пути, ненулевые минимумы, все крайние координаты, IRQ и нативный запуск не доказаны'])}
TARGETS={0xE1EB:'D3D.PreviewClipCases.Entry',0xC24F:'PreviewClipCorners.Value.SeenFlags'}
for (region,a),label in LABELS.items():TARGETS[a]='D3D.PreviewClipCases.'+label
for prefix,entries in (
 ('BuildPreviewClip',((0xE5E8,'TopProduct.Entry'),(0xE5F3,'TopProduct.FromDelta'),(0xE607,'BottomProduct.Entry'),(0xE612,'BottomProduct.FromDelta'),(0xE626,'LeftProduct.Entry'),(0xE645,'RightProduct.Entry'))),
 ('AppendPreviewClip',((0xE664,'TopIntersection.Entry'),(0xE667,'TopIntersection.FromProduct'),(0xE6AF,'BottomIntersection.Entry'),(0xE6B2,'BottomIntersection.FromProduct'),(0xE6FA,'LeftIntersection.Entry'),(0xE6FD,'LeftIntersection.FromProduct'),(0xE757,'RightIntersection.Entry'),(0xE75A,'RightIntersection.FromProduct'),(0xE7B4,'TopLeft.Entry'),(0xE7BF,'TopRight.Entry'),(0xE7CA,'BottomLeft.Entry'),(0xE7D5,'BottomRight.Entry'),(0xE846,'Second.Entry'))),
 ('SubtractPreviewClip',((0xE7E0,'TopLeft.Entry'),(0xE7F4,'TopRight.Entry'),(0xE808,'BottomLeft.Entry'),(0xE81C,'BottomRight.Entry'),(0xE830,'Columns.Entry'),(0xE83B,'Rows.Entry')))):
 for a,suffix in entries:TARGETS[a]='D3D.'+prefix+suffix
TARGETS[0xE85D]='D3D.UnwindPreviewClipFrame.Entry'


def name_operands(region,address,operation):
 if region!='D3D' or address!=0xE1EB:return operation
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)],operation)
 for bit,name in enumerate(('BottomRight','BottomLeft','TopRight','TopLeft')):
  for opcode in ('BIT','SET'):operation=operation.replace(opcode+' '+str(bit)+', (HL)',opcode+' @MapClipCornerBit.'+name+', (HL)')
 return operation
