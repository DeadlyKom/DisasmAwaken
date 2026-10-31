"""Диспетчер отдельного сегмента, обмен концов и три исходных CPU-возврата."""
from pathlib import Path
import json,re
FUNCTIONS={0xEAB6:('DispatchPreviewClipSegment','Перестановка внутреннего первого конца и табличное отсечение отдельного сегмента')}
ENDS={0xEAB6:0xEB10}
LABELS={('D3D',0xEAE9):'PickCase',('D3D',0xEB08):'Return'}
DOCUMENTS={('D3D',0xEAB6):('PreviewClipSegment','перестановка двух полных записей, точный вход обработчика и общий эпилог CP 4')}
CONST_MODULE='PreviewClipDispatchConst'
CONSTANTS=(('InsideCode',0xF0,'полный код внутренней точки, только точное равенство включает обмен'),
 ('ComplementMask',0xF0,'маска дополнения к коду сторон первого конца'),('SideMask',0x0F,'младшие разряды сторон второго конца'),
 ('LowTablePage',0xCC,'страница младших байтов целей, старшие читаются на следующей странице'),
 ('BlockCorners',1,'ненулевой режим подавления отдельных углов'),('TwoPointBytes',4,'байтовый размер ровно двух выходных точек'))
DATA_WRITES={a:(size,'Source/D3D/Data/'+owner+'.asm') for a,size,owner in (
 (0xC250,1,'PreviewClipCorners'),(0xC230,1,'PreviewClipFirst'),(0xC240,1,'PreviewClipSecond'),(0xC23C,2,'PreviewClipSecond'),
 (0xC22C,2,'PreviewClipFirst'),(0xC23E,2,'PreviewClipSecond'),(0xC22E,2,'PreviewClipFirst'),(0xC22B,1,'PreviewContourSize'))}
root=Path(__file__).resolve().parents[3]
cases=json.loads((root/'Tools/Disasm/Reports/PreviewClipDecisionPaths.json').read_text('utf-8'))['cases']
INDIRECT_TARGETS={0xEB07:tuple(sorted({c['entry'] for c in cases if c['first']!=0 or c['second']==0}))}
CONTRACTS={('D3D',0xEAB6):(
 ['HL, DE, BC и AF произвольный исходный контекст, параметры читаются из PreviewClipFirst и PreviewClipSecond',
  "HL', DE', BC' сохраняются, AF' и IX рабочий контекст арифметики, IY сохраняется",
  'два физических конца содержат слова координат и согласованные полные коды сторон',
  'D3D подключён в банке 4, E011 настроил операнды границ, страницы CC/CD содержат исходные цели',
  'под CPU-SP доступны байты трёх подставных возвратов и вложенных вызовов, обычный адрес возврата доступен',
  'все фактически исполненные деления имеют ненулевой знаменатель и допустимое слово частного'],
 ['HL и BC обычного выхода равны контексту последнего действия обработчика, DE=Return, A=ByteCount, F от CP 4',
  'специальный выход даёт HL=EBF2, DE рабочий, BC=00EA, AF=EBA9, A=EB не является размером',
  "HL', DE', BC' сохранены, AF' и IX определяются исполненным путём, IY сохранён",
  'при полном коде первого конца F0 две пятибайтовые записи меняются местами, иначе остаются на своих местах',
  'BlockCode=1, ByteCount содержит размер результата 0, 2 или 4 в проверенной геометрической области',
  'младшая тетрада SeenFlags может получать отметки углов, старшая сохраняется, выбранные кэши обновляются',
  'SP после окончательного возврата равен входному+2, I, IFF и IM сохраняются'],
 ["HL, DE, BC, AF, AF', IX по выбранному пути, оба конца при обмене, BlockCode, SeenFlags, ByteCount, кэши, страница C8 и CPU-стек"],
 ['непосредственно перед JP HL равен цели, DE=EB08, BC имеет входной C, B равен F0 при обмене либо входному B',
  'входной AF обработчика содержит A=индекс таблицы, F=88 от INC H страницы CC в CD',
  'индекс равен ((NOT код первого) AND F0) OR (код второго AND 0F) после возможной перестановки',
  'три слова EB08 расположены под входным SP, обычный эпилог снимает два оставшихся слова, специальный снимает все три',
  'CP 4 устанавливает Z только для двух точек, Carry устанавливается для размера 0 или 2',
  'два внутренних конца дают одну выходную точку, размер 2 и Carry=1, полноценным отрезком такой результат не считается',
  'состояние SeenFlags перед обработчиком сохраняется, оно здесь не обнуляется',
  'префикс проверен в 20736 контекстах, геометрия в 534160 случаях, все конечные регистры всех путей не заявлены'])}
COMMENTS={
 0xEAB6:(['установка ненулевого режима, отдельные угловые точки сегменту не добавляются'],None),
 0xEABB:(['проверка полного кода первого конца на точное внутреннее значение F0'],None),
 0xEAC0:([],'переход, если полный код первого конца не равен F0, сохранить порядок концов'),
 0xEAC2:(['-----------------------------------------','Обмен двух полных пятибайтовых записей','-----------------------------------------','сохранение внутреннего кода и перестановка кодов сторон'],None),
 0xEACD:(['обмен координатными словами колонок, флаги сравнения сохраняются'],None),
 0xEADB:(['обмен координатными словами строк без изменения флагов'],None),
 0xEAE9:(['-----------------------------------------','Индекс таблицы и CPU-кадр','-----------------------------------------','обнуление байтового размера нового результата'],None),
 0xEAED:(['расчёт старшей тетрады индекса из дополнения к коду первого конца'],None),
 0xEAF4:(['расчёт младшей тетрады по коду сторон второго конца'],None),
 0xEAFB:(['поиск двух байтов цели на страницах CC и CD'],None),
 0xEAFE:(['переход к странице старших байтов, итоговый F=88 от INC H при Carry=0'],None),
 0xEB01:(['создание трёх одинаковых подставных CPU-возвратов для общего и специального выходов'],None),
 0xEB07:(['передача управления фактической цели таблицы без четвёртого слова возврата'],None),
 0xEB08:(['-----------------------------------------','Обычный эпилог сегмента','-----------------------------------------','чтение результата и снятие двух оставшихся подставных возвратов'],None),
 0xEB0D:(['проверка размера ровно из двух точек, флаги возвращаются внешнему конвейеру'],None)}
TARGETS={0xC250:'PreviewClipCorners.Value.BlockCode',0xC230:'PreviewClipFirst.Value.Outcode',0xC240:'PreviewClipSecond.Value.Outcode',
 0xC22C:'PreviewClipFirst.Value.SecondAxis',0xC23C:'PreviewClipSecond.Value.SecondAxis',0xC22E:'PreviewClipFirst.Value.FirstAxis',0xC23E:'PreviewClipSecond.Value.FirstAxis',
 0xC22B:'PreviewContourSize.Value.ByteCount',0xEAE9:'D3D.DispatchPreviewClipSegment.PickCase',0xEB08:'D3D.DispatchPreviewClipSegment.Return'}


def name_operands(region,address,operation):
 if region!='D3D' or address!=0xEAB6:return operation
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)],operation)
 return operation.replace('LD A, #01','LD A, @PreviewClipDispatchConst.BlockCorners').replace('CP #F0','CP @PreviewClipDispatchConst.InsideCode').replace('AND #F0','AND @PreviewClipDispatchConst.ComplementMask').replace('AND #0F','AND @PreviewClipDispatchConst.SideMask').replace('LD H, #CC','LD H, @PreviewClipDispatchConst.LowTablePage').replace('CP #04','CP @PreviewClipDispatchConst.TwoPointBytes')
