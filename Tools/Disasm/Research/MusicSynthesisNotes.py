"""Привязка предметных пояснений к проверенным блокам синтеза, без пересказа мнемоник."""
import re
from MusicGateTickFacts import COMMENTS as GATE_COMMENTS


def build(functions,instructions,facts):
 notes=dict(GATE_COMMENTS)
 def before(address,text):notes[address]=([text],None)
 def condition(address,text):notes[address]=([],text)
 for start,p,addresses in zip(facts.SYNTH_STARTS,facts.PROFILES,facts.ROLE_ADDRESSES):
  finish=(0xE0CD,0xE1CD,0xE2CB)[facts.SYNTH_STARTS.index(start)];rows=[i for i in instructions if start<=i['address']<finish];role=dict(zip(facts.ROLE_NAMES,addresses));name=p['name']
  before(start,'подготовка кадровых накопителей и сохранение настоящего SP' if name=='A' else 'проверка числового состояния разрешения синтеза '+name)
  for label,text in (
   ('StoreSamplePos','сохранение следующей позиции сэмпла, текущий шаг адресуется по прежней позиции'),
   ('LimitAdjust','ограничение увеличения поправки уровня сравнением с 31'),('StoreAdjust','учёт переноса для увеличения либо подавления выхода за нулевую поправку'),
   ('ApplyBias','расчёт уровня как базового значения плюс поправка минус 16'),('ClampLevel','ограничение уровня диапазоном 0..15'),
   ('ScaleVolume','применение строки исходной таблицы громкости через байтовое смещение'),
   ('SaveLevel','сохранение рассчитанного уровня и его флагов в альтернативном AF'),
   ('SetNoise','замена текущего вклада шума значением канала '+name),
   ('EnvelopeDelta','расширение знака пятибитового вклада огибающей'),('AddEnvelopeBias','прибавление накопленного вклада огибающей по модулю 256'),
   ('AddToEnvelope','добавление вклада канала к общему восьмибитовому периоду в альтернативном L'),
   ('MixerBits','формирование битов текущего канала в микшере'),
   ('ReadOrnament','сохранение текущей тональной поправки в DE и переход к заголовку орнамента'),
   ('StoreOrnPos','сохранение следующей позиции орнамента, текущий байт ещё берётся по прежней'),
   ('ReadPitch','выбор слова периода по индексу ноты, SP временно указывает на таблицу'),
   ('LimitTarget','расчёт периода для проверки достижения цели с уже обновлённым смещением'),
   ('CompareLimit','сравнение расчётного и целевого периодов с учётом направления из CP')):before(role[label],text)
  before(role['StoreSamplePos']+3,'расчёт смещения шага, второе удвоение затрагивает только L и теряет перенос' if name!='C' else 'расчёт смещения шага умножением полного слова позиции на четыре')
  for n,i in enumerate(rows):
   op=i['operation'];address=i['address'];previous=rows[n-1]['operation'] if n else '';target=None
   m=re.fullmatch(r'(JR|JP) (Z|NZ|C|NC|M),#([0-9A-F]{4})',op)
   if m:target=int(m[3],16)
   if op=='LD SP,#0000':before(address,'чтение циклического заголовка '+('сэмпла' if address<p['sample_pos'] else 'орнамента')+' через временный SP')
   if op=='CP D':before(address,'проверка следующей позиции сэмпла относительно FMusicLoopHeader.Length')
   if op=='CP B':before(address,'проверка следующей позиции орнамента относительно FMusicLoopHeader.Length')
   if op=='ADD A,(HL)':before(address,'расчёт байтовой суммы текущей ноты и орнамента с оборачиванием')
   if op=='BIT 5,D':before(address,'проверка AccumShiftBit, нужно ли сохранять вклад для следующих кадров')
   if op=='BIT 6,D':before(address,'проверка AccumToneBit, нужно ли сохранять тональную поправку')
   if op=='LD BC,#0000':before(address,'чтение прежнего накопленного смещения тона перед записью периода')
   if address==p['target']-1:before(address,'чтение целевой ноты для получения её слова периода')
   if address==p['note']-1:before(address,'проверка направления по целевой и текущей нотам')
   if op=='DEC A' and p['counter']<address<role['LimitTarget']:before(address,'расчёт уменьшенного счётчика тонального скольжения')
   if op=='LD HL,#0000' and address>p['counter']:before(address,'чтение слова шага и прибавление к прежнему SlideOffset')
   if op.startswith('LD (#') and op.endswith(',HL'):
    if int(op[5:9],16)==p['slide']:before(address,'сохранение старшего байта разности с нулевым младшим после достижения цели' if address>role['LimitTarget'] else 'сохранение нового накопленного смещения, текущий тон уже записан')
    if int(op[5:9],16)==0xDC00+2*facts.SYNTH_STARTS.index(start):before(address,'запись периода текущего канала до обновления шага скольжения')
   if op.startswith('LD (#') and op.endswith(',A') and int(op[5:9],16)==p['note']:before(address,'замена текущей ноты целевой после достижения ограничения')
   if not m:continue
   if target==finish+6:condition(address,'переход, если состояние канала равно FF, передать нулевую амплитуду без чтения ресурсов')
   elif target==role['StoreSamplePos']:condition(address,'переход, если следующая позиция сэмпла меньше Length, сохранить её без зацикливания')
   elif target==role['ApplyBias']:condition(address,'переход, если AdjustBit равен нулю, сохранить поправку уровня')
   elif target==role['LimitAdjust']:condition(address,'переход, если AdjustUpBit установлен, увеличивать поправку до 31')
   elif target==role['ClampLevel']:condition(address,'переход, если базовый уровень с поправкой не меньше 16, проверить верхний предел')
   elif target==role['ScaleVolume']:condition(address,'переход, если уровень меньше 16, применить строку таблицы')
   elif target==role['SaveLevel']:condition(address,'переход, если FixedLevelBit установлен, сохранить уровень без добавления маски огибающей')
   elif target==role['EnvelopeDelta']:condition(address,'переход, если EnvShiftBit установлен, рассчитать вклад огибающей')
   elif target in (role['SetNoise'],role['AddToEnvelope']):condition(address,'переход, если AccumShiftBit равен нулю, использовать вклад только в текущем кадре')
   elif target==role['AddEnvelopeBias']:condition(address,'переход, если пятибитовый вклад меньше 16, сохранить неотрицательное значение')
   elif target==role['ReadOrnament']:condition(address,'переход, если AccumToneBit равен нулю, оставить прежний накопитель тона')
   elif target==role['StoreOrnPos']:condition(address,'переход, если следующая позиция орнамента меньше Length, сохранить её без зацикливания')
   elif target==role['ReadPitch']:condition(address,'переход, если байтовая сумма ноты и орнамента меньше 128, использовать её индекс')
   elif target==finish+5:condition(address,'переход, если результат DEC счётчика скольжения отрицателен, оставить его без записи')
   elif target==finish+2:condition(address,'переход, если уменьшенный счётчик ненулевой, сохранить его без добавления шага')
   elif target==role['CompareLimit']:condition(address,'переход, если целевая нота не меньше текущей, вычитать расчётный период из целевого')
   elif target==finish:condition(address,'переход, если вычитание дало заём, продолжить скольжение с перезагрузкой')
   else:raise AssertionError(('unexplained_synthesis_condition',hex(address),op))
 for finish in (0xE0CD,0xE1CD):
  before(finish,'чтение перезагрузки счётчика тонального скольжения')
  before(finish+2,'сохранение перезагрузки либо уже уменьшенного счётчика скольжения')
  before(finish+5,'восстановление амплитуды и её флагов обменом с альтернативным AF')
 return notes
