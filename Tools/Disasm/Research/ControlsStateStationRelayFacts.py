"""Перенесённый вход 4200, исходный код DD23, восстановление 481 байта после загрузки станции."""
TAG='ControlsStateStationRelay'
TITLE='перенесённая загрузка STATIONF с восстановлением состояния'
SLOT,REGION=23,'Controls'
CASES=768
FUNCTIONS={0x4200:('LoadStationStateRelay','Загрузка STATIONF с условным восстановлением 481 байта в состояние станции и переходом в свежий загрузчик')}
ENDS={0x4200:0x4231}
KEYS={}
LOCAL={0x421F:'AfterLoad'}
MUTATIONS=()
LOCATION='копия в фиксированной RAM, исходный адрес DD23 банка 1'


def file_offset(address):return 0x245+address-0x4200


CONTRACTS={('Controls',0x4200):(
 ['HL, DE, BC и AF числовых аргументов не задают, PrepareStationReload перенёс 256 исходных байтов в 4200..42FF',
  'родитель сохранил 512 байтов состояния по 4000, его перестановка LowPairs уже включена в сохранённые байты',
  'ключ STATIONFC доступен по 4231..4239, системные поля TR-DOS и Dispatch доступны, paging разблокирован',
  'для продолжения требуется успешная внешняя загрузка STATIONF по 6000 с сохранением копии и буфера, SP имеет место для CALL'],
 ['OUT 7FFD получает 18, IY=5C3A, девять байтов ключа копируются в 5CDD, 5CF9 получает ноль',
  'CALL TrDos.Dispatch получает C=0E и слово возврата 421F на текущем CPU-стеке',
  'на границе вызова HL=423A, DE=5CE6, BC=000E, AF=0044, SP=входной SP-2, IX, I, IM и IFF сохраняются',
  'AfterLoad повторяет DI, ровно 481 байт из 4000..41E0 копируется в 983B..9A1B состояния свежей станции',
  'последние 31 байт сохранённых родителем 512 не восстанавливаются, объём не расширен по аналогии',
  'SP получает 5FFF, JP ведёт в StationBoot.RelocateBootstrap свежего STATIONF по 6300, Carry от TR-DOS не проверяется',
  'на конечной границе HL=41E1, DE=9A1C, BC=0, A сохранён от TR-DOS, F сохраняет S/Z/Carry и получает прочие биты по LDIR, IFF=0',
  'IX, IY, I, IM, альтернативные регистры и paging после TR-DOS сохраняют его внешний результат, старый адрес возврата не используется'],
 ['HL, DE, BC, AF, IY до вызова, SP, IFF после вызова, R, ключ запроса, 5CF9, 481 байт состояния станции, временное слово CALL и paging до вызова, далее внешние эффекты TR-DOS'],
 ['сама стадия не устанавливает I и IM, до вызова они обеспечены родительским PrepareStationReload',
  'общая серия 768 сценариев двух стадий включает 256 исполнений этого входа до TR-DOS и 256 условных успешных возвратов',
  'сверены восемь банков RAM и кратность записей, основные и сохраняемые регистры, I, IM, IFF и SP',
  'успешная загрузка подставлена явно и не выдаётся за исполнение TR-DOS, полные R, такты и конечный F в этой серии не сверялись',
  'в отдельном сквозном прогоне ROM загружает STATIONF, проверены 481 восстановленный байт и 31 байт свежего состояния',
  '[профиль с дисковым ROM](../../Docs/StationFlightCycle.md#сквозной-прогон-с-rom-tr-dos)'])}
COMMENTS={
 0x4200:(['Выбор банка 0 с теневым экраном перед файловым запросом станции.'],None),
 0x4207:(['Установка системного IY без изменения I, IM и IFF, они подготовлены вызывающим кодом.'],None),
 0x420B:(['Копирование девятибайтового ключа STATIONF с типом C из перенесённой копии.'],None),
 0x4216:(['Выбор нулевого диска, затем файловая операция 0E через настоящий CALL.'],None),
 0x421F:(['Внешнее продолжение после TR-DOS, условие успешной загрузки задано отдельно, Carry не проверяется.'],None),
 0x4220:(['Восстановление ровно 481 байта в контекст станции, оставшиеся 31 байт копии родителя не переносятся.'],None),
 0x422B:(['Замена стека и переход в загрузчик свежего STATIONF, прежняя рамка не восстанавливается.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Controls',0x4200):return operation
    for before,after in {'LD BC, #7FFD':'LD BC, @Hardware.PagingPort',
      'LD BC, #0009':'LD BC, @FTrDosFileKey','LD HL, #4231':'LD HL, @ControlsStateStationKey.Value.Name','CALL #3D13':'CALL @TrDos.Dispatch',
      'JP #6300':'JP @StationBoot.RelocateBootstrap.Entry'}.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    import json
    path=root/'Tools/Disasm/Research/Analyze.py';text=path.read_text('utf-8');needle='BLOCKS = [\n';assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+'    # Копия по LDIR Controls.PrepareStationReload, длина переноса 100.\n    block(23, 0x245, 0x100, 0x4200, "Controls", (0x4200,)),\n').encode('utf-8')
    path=root/'Tools/Disasm/Reports/ControlFlow.json';value=json.loads(pending[path]);group=next(r for r in value if r['name']=='Controls')
    group['blocks'].append(dict(slot=23,offset=0x245,length=256,origin=0x4200,name='Controls',roots=[0x4200]))
    group['unresolved']+=[dict(address=0x421C,operation='CALL #3D13',target=0x3D13,bank=0,reason='внешний TR-DOS'),
      dict(address=0x422E,operation='JP #6300',target=0x6300,bank=0,reason='вход свежезагруженного STATIONF')]
    pending[path]=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
