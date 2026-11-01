"""Локальные факты о счётчиках, общий синтез содержащих их фрагментов ещё не доказан."""
PROFILES=(('A',0xE0D3,0xE0ED,0xDC08,0xE0D7,0xDFEF,0xE0E5,0xE0E9,0xE0CD),('B',0xE1D3,0xE1ED,0xDC09,0xE1D7,0xE0EE,0xE1E5,0xE1E9,0xE1CD),('C',0xE2D1,0xE2EB,0xDC0A,0xE2D5,0xE1EE,0xE2E3,0xE2E7,0xE2CB))
FIELDS={};COMMENTS={}
for name,start,stop,amplitude,counter,state,disabled,enabled,parent in PROFILES:
 for suffix,address,note in (('Amplitude',amplitude,'буфер амплитуды AY'),('Counter',counter,'текущий счётчик чередования'),('State',state,'полный байт состояния, 00 разрешает синтез, FF пропускает его'),('DisabledTicks',disabled,'перезагрузка после получения ненулевого состояния'),('EnabledTicks',enabled,'перезагрузка после получения нулевого состояния')):
  FIELDS[suffix+name]=(address,note+' канала '+name)
 COMMENTS.update({
  start:(['запись рассчитанной амплитуды в буфер AY канала '+name],None),
  start+3:(['чтение текущего счётчика чередования канала '+name],None),
  start+5:(['расчёт уменьшенного счётчика с байтовым оборачиванием'],None),
  start+6:([],'переход, если результат DEC отрицателен, сохранить счётчик и продолжить синтез'),
  start+9:([],'переход, если счётчик после DEC ненулевой, записать уменьшенное значение'),
  start+11:(['формирование FF для переключения всего байта состояния'],None),
  start+15:(['инверсия полного байта состояния после истечения счётчика'],None),
  start+17:(['выбор перезагрузки для нового ненулевого состояния'],None),
  start+19:([],'переход, если новое состояние ненулевое, использовать длительность выключенного состояния'),
  start+21:(['выбор перезагрузки для нового нулевого состояния'],None),
  start+23:(['сохранение уменьшенного либо перезагруженного счётчика'],None)})


def name_operands(region,address,operation):
 if region=='Music' and address in {p[-1] for p in PROFILES}:
  for name,(a,note) in FIELDS.items():operation=operation.replace('(#'+format(a,'04X')+')','(@MusicGateState.'+name+')')
 return operation
