"""Отложенные длительности и позиции сэмпла и орнамента канала A."""
FUNCTIONS={0xDE90:('StageGateAndSampleA','Применение отложенных длительностей чередования и позиции сэмпла канала A'),0xDEAE:('StageOrnamentA','Применение отложенной позиции орнамента канала A')}
END_OFFSETS={0xDE90:0x3AE,0xDEAE:0x3B9}
DOCUMENT='MusicChannelStaging'
CONTINUATIONS={0xDE90:('StageOrnamentA',0xDEAE),0xDEAE:('StageChannelBRow',0xDEB9)}
LABELS={('Music',0xDEA3):'ApplySample'}
OLD_LABELS={'UnknownDE90.PointDEA3':'StageGateAndSampleA.ApplySample'}
CONTRACTS={('Music',0xDE90):(
 ['HL, DE и C сохраняются, E=18 требуется для восстановления JR после отложенной команды',
  'B и AF могут сохраняться на пути без команд, оба переключателя содержат 18 либо 06',
  'параметры EnabledTicks, DisabledTicks и SamplePosition подготовлены писателями команд в доступном банке MUZ1'],
 ['граница блока находится в StageOrnamentA по DEAE, собственного RET нет',
  'при GateCommand=06 он получает E, EnabledTicks записан в GateEnabled и GateCounter, DisabledTicks в GateDisabled',
  'при SampleCommand=06 SamplePosition записан в SampleCursor, SampleCommand получает E',
  'при команде позиции A=E, B=09, иначе при команде длительности A=DisabledTicks, B=11',
  'если обе команды выключены, A и B сохранены, HL, DE, C и F сохранены во всех путях',
  'альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до границы следующего блока'],
 ['BC только B, AF только A, GateCommand, GateEnabled, GateDisabled, GateCounter, SampleCommand, SampleCursor, R'],
 ['команды восстанавливают JR только при штатном E=18, это не обычные флаги данных',
  'команда длительностей не меняет текущее разрешение канала DFEF, текущий счётчик всегда получает EnabledTicks',
  'нулевые длительности и произвольная позиция сэмпла копируются без проверки его заголовка']),
 ('Music',0xDEAE):(
 ['HL, DE и C сохраняются, E=18 требуется для восстановления JR',
  'B и AF сохраняются при выключенной команде, OrnamentCommand содержит 18 либо 06',
  'OrnamentPos является подготовленным байтом позиции орнамента в доступном банке MUZ1'],
 ['граница блока находится по DEB9, собственного RET нет',
  'при OrnamentCommand=06 OrnamentPos записан в OrnamentCursor, OrnamentCommand получает E, A=E, B=09',
  'при OrnamentCommand=18 A и B сохранены, HL, DE, C и F сохранены во всех путях',
  'альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до границы следующего блока'],
 ['BC только B, AF только A, OrnamentCommand, OrnamentCursor, R'],
 ['исходный JR пропускает тело, код 06 включает LD B,09 с сохранением длины команды',
  'значение позиции копируется без проверки длины орнамента, его последующий синтез проверяется отдельно'])}
COMMENTS={
 0xDE90:(['изменяемый JR пропускает команду длительностей, код 06 открывает её тело'],None),
 0xDE92:(['выключение однократной команды кодом JR из E'],None),
 0xDE96:(['чтение длительности включённого состояния и запуск текущего счётчика тем же байтом'],None),
 0xDE9E:(['чтение длительности выключенного состояния для последующего чередования'],None),
 0xDEA3:(['изменяемый JR пропускает команду позиции сэмпла, код 06 открывает её тело'],None),
 0xDEA5:(['перенос ожидающей позиции сэмпла в курсор синтеза канала A'],None),
 0xDEAA:(['выключение однократной команды позиции сэмпла кодом JR из E'],None),
 0xDEAE:(['изменяемый JR пропускает команду позиции орнамента, код 06 открывает её тело'],None),
 0xDEB0:(['перенос ожидающей позиции орнамента в курсор синтеза канала A'],None),
 0xDEB5:(['выключение однократной команды позиции орнамента кодом JR из E'],None)}
FIELDS={
 'GateCommand':(0xDE90,'код команды длительностей, 18 пропускает тело, 06 включает его'),
 'EnabledTicks':(0xDE97,'ожидающая длительность включённого состояния'),
 'DisabledTicks':(0xDE9F,'ожидающая длительность выключенного состояния'),
 'SampleCommand':(0xDEA3,'код отложенной установки позиции сэмпла'),
 'SamplePosition':(0xDEA6,'ожидающая байтовая позиция сэмпла'),
 'OrnamentCommand':(0xDEAE,'код отложенной установки позиции орнамента'),
 'OrnamentPos':(0xDEB1,'ожидающая байтовая позиция орнамента'),
 'GateEnabled':(0xE0E9,'длительность после перехода в включённое состояние'),
 'GateDisabled':(0xE0E5,'длительность после перехода в выключенное состояние'),
 'GateCounter':(0xE0D7,'текущий счётчик до переключения разрешения канала A'),
 'SampleCursor':(0xDFFA,'позиция шага сэмпла, используемая синтезом A'),
 'OrnamentCursor':(0xE07C,'позиция байта орнамента, используемая синтезом A')}
FIELD_MODULE='MusicChannelAState'


def name_operands(region,address,operation):
 if region=='Music' and address in FUNCTIONS:
  for name,(a,note) in FIELDS.items():operation=operation.replace('(#'+format(a,'04X')+')','(@'+FIELD_MODULE+'.'+name+')')
  operation=operation.replace('JR #DEA3','JR @Music.StageGateAndSampleA.ApplySample').replace('JR #DEAE','JR @Music.StageOrnamentA.Entry').replace('JR #DEB9','JR @Music.StageChannelBRow.Entry')
 return operation
