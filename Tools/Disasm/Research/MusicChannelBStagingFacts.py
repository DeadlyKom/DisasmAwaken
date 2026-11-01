"""Три последовательных блока отложенных параметров канала B."""
from MusicChannelAStagingFacts import FIELDS as A_FIELDS
FUNCTIONS={0xDF1E:('StageGateB','Применение отложенных длительностей чередования канала B'),0xDF31:('StageSampleB','Применение отложенной позиции сэмпла канала B'),0xDF3C:('StageOrnamentB','Применение отложенной позиции орнамента канала B')}
END_OFFSETS={0xDF1E:0x431,0xDF31:0x43C,0xDF3C:0x447}
DOCUMENT='MusicChannelStaging'
CONTINUATIONS={0xDF1E:('StageSampleB',0xDF31),0xDF31:('StageOrnamentB',0xDF3C),0xDF3C:('StageEnvelopeAndNoise',0xDF47)}
LABELS={}
MAPPING={0xDE90:0xDF1E,0xDE97:0xDF25,0xDE9F:0xDF2D,0xDEA3:0xDF31,0xDEA6:0xDF34,0xDEAE:0xDF3C,0xDEB1:0xDF3F,0xE0E9:0xE1E9,0xE0E5:0xE1E5,0xE0D7:0xE1D7,0xDFFA:0xE0F9,0xE07C:0xE17C}
FIELDS={name:(MAPPING[a],note.replace('канала A','канала B')) for name,(a,note) in A_FIELDS.items()}
FIELD_MODULE='MusicChannelBState'
COMMON_IN=['HL, DE и C сохраняются, E=18 требуется для восстановления JR после отложенной команды',
 'B и AF сохраняются при выключенной команде, переключатель содержит 18 либо 06',
 'параметр команды подготовлен в доступном для записи банке MUZ1, прерывания запрещены согласно кадровому входу']
COMMON_OUT=['HL, DE, C и F сохранены, альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до следующего блока',
 'при выключенной команде A и B сохранены, штатный E=18 выключает применённую команду восстановлением JR']
CONTRACTS={('Music',0xDF1E):(COMMON_IN,
 ['граница блока находится в StageSampleB по DF31, собственного RET нет',
  'при GateCommand=06 он получает E, EnabledTicks записан в GateEnabled и GateCounter, DisabledTicks в GateDisabled',
  'при выполненной команде A=DisabledTicks, B=11']+COMMON_OUT,
 ['BC только B, AF только A, GateCommand, GateEnabled, GateDisabled, GateCounter, R'],
 ['команда не меняет текущее разрешение канала E0EE, счётчик всегда запускается значением EnabledTicks',
  'нулевые длительности копируются без нормализации, дальнейшее поведение задаёт DEC счётчика']),
 ('Music',0xDF31):(COMMON_IN,
 ['граница блока находится в StageOrnamentB по DF3C, собственного RET нет',
  'при SampleCommand=06 SamplePosition записан в SampleCursor, SampleCommand получает E, A=E, B=09']+COMMON_OUT,
 ['BC только B, AF только A, SampleCommand, SampleCursor, R'],
 ['позиция сэмпла копируется без проверки его заголовка, последующий синтез не входит в локальный договор']),
 ('Music',0xDF3C):(COMMON_IN,
 ['граница блока находится в StageEnvelopeAndNoise по DF47, собственного RET нет',
  'при OrnamentCommand=06 OrnamentPos записан в OrnamentCursor, OrnamentCommand получает E, A=E, B=09']+COMMON_OUT,
 ['BC только B, AF только A, OrnamentCommand, OrnamentCursor, R'],
 ['позиция орнамента копируется без проверки его заголовка, последующий синтез не входит в локальный договор'])}
COMMENTS={
 0xDF1E:(['изменяемый JR пропускает команду длительностей B, код 06 открывает её тело'],None),
 0xDF20:(['выключение однократной команды длительностей кодом JR из E'],None),
 0xDF24:(['перенос длительности включённого B в перезагрузку и текущий счётчик'],None),
 0xDF2C:(['перенос длительности выключенного B в отдельную перезагрузку'],None),
 0xDF31:(['изменяемый JR пропускает команду позиции сэмпла B, код 06 открывает её тело'],None),
 0xDF33:(['перенос ожидающей позиции сэмпла в курсор синтеза канала B'],None),
 0xDF38:(['выключение однократной команды позиции сэмпла кодом JR из E'],None),
 0xDF3C:(['изменяемый JR пропускает команду позиции орнамента B, код 06 открывает её тело'],None),
 0xDF3E:(['перенос ожидающей позиции орнамента в курсор синтеза канала B'],None),
 0xDF43:(['выключение однократной команды позиции орнамента кодом JR из E'],None)}


def name_operands(region,address,operation):
 if region=='Music' and address in FUNCTIONS:
  for name,(a,note) in FIELDS.items():operation=operation.replace('(#'+format(a,'04X')+')','(@'+FIELD_MODULE+'.'+name+')')
  operation=operation.replace('JR #DF31','JR @Music.StageSampleB.Entry').replace('JR #DF3C','JR @Music.StageOrnamentB.Entry').replace('JR #DF47','JR @Music.StageEnvelopeAndNoise.Entry')
 return operation
