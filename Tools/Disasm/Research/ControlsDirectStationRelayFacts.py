"""Перенесённый вход 4000, исходный код по DCA9, возврат файловой службы непосредственно в 6300."""
TAG='ControlsDirectStationRelay'
TITLE='прямая перенесённая загрузка STATIONF'
SLOT,REGION=23,'Controls'
CASES=768
FUNCTIONS={0x4000:('LoadStationDirectRelay','Перенесённый запрос STATIONF с внешним возвратом TR-DOS непосредственно в загрузчик станции по 6300')}
ENDS={0x4000:0x4031}
KEYS={}
LOCAL={}
MUTATIONS=()
LOCATION='копия в фиксированной экранной RAM, исходный адрес DCA9 банка 1'


def file_offset(address):return 0x1CB+address-0x4000


CONTRACTS={('Controls',0x4000):(
 ['HL, DE, BC и AF числовых аргументов не задают, RelocateStationReload перенёс исходные 256 байтов в 4000..40FF',
  'ключ STATIONFC доступен по 4031..4039, системные поля TR-DOS и его Dispatch доступны, paging разблокирован',
  'для штатной передачи требуется успешная внешняя загрузка STATIONF по 6000 с доступным новым входом 6300'],
 ['DI сбрасывает IFF, IM=1, I=3F, IY=5C3A, OUT 7FFD получает 1F и затем 18, итоговая страница 18',
  'SP получает 5FFF, девять байтов ключа копируются в 5CDD, 5CF9 получает ноль',
  'PUSH DE помещает 6300 по 5FFD, затем JP TrDos.Dispatch передаёт C=0E без рамки CALL',
  'на границе PC=3D13 HL=403A, DE=6300, BC=000E, AF=0044, SP=5FFD, IX и альтернативные регистры сохранены',
  'обычный возврат внешней файловой службы снимет 6300, локального продолжения проверки результата нет',
  'при успешной загрузке это StationBoot.RelocateBootstrap свежего STATIONF, исходный стек вызывающего не восстанавливается'],
 ['HL, DE, BC, AF, IY, SP, I, IM, IFF, R, ключ запроса, 5CF9, два байта нового стека и paging, далее внешние эффекты TR-DOS'],
 ['стадия не восстанавливает сохранённый полётный блок, этим отличается от LoadStationStateRelay по 4200',
  'общая серия 768 сценариев двух стадий включает 256 исполнений этой стадии до границы TR-DOS',
  'сверены восемь банков RAM и кратность записей, основные и сохраняемые регистры, I, IM, IFF и SP',
  'при отсутствии STATIONF в модели TR-DOS 5.04T возвращает #5D0F=1 на #6300 прежнего ACTION',
  'успешный путь загружает 160 секторов, берёт 512 байтов состояния станции из файла и начинает первый кадр'])}
COMMENTS={
 0x4000:(['Запрет прерываний перед установкой системного контекста для загрузки станции.'],None),
 0x400B:(['Выбор страницы 1F и затем 18 исходными OUT, защёлка paging не блокируется.'],None),
 0x4016:(['Замена старого стека системной вершиной, возврата в прежнюю рамку нет.'],None),
 0x4019:(['Копирование девятибайтового ключа STATIONF с типом C из перенесённой копии.'],None),
 0x4024:(['Выбор нулевого диска перед файловым запросом.'],None),
 0x4028:(['Создание слова 6300 на новом стеке для непосредственного внешнего возврата TR-DOS.'],None),
 0x402C:(['Передача файловой операции 0E без локального CALL и проверки результата.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Controls',0x4000):return operation
    for before,after in {'LD BC, #7FFD':'LD BC, @Hardware.PagingPort',
      'LD BC, #0009':'LD BC, @FTrDosFileKey','LD HL, #4031':'LD HL, @ControlsDirectStationKey.Value.Name','JP #3D13':'JP @TrDos.Dispatch',
      'LD DE, #6300':'LD DE, @StationBoot.RelocateBootstrap.Entry'}.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    import json
    path=root/'Tools/Disasm/Research/Analyze.py';text=path.read_text('utf-8');needle='BLOCKS = [\n';assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+'    # Копия по LDIR Controls.RelocateStationReload, длина переноса 100.\n    block(23, 0x1CB, 0x100, 0x4000, "Controls", (0x4000,)),\n').encode('utf-8')
    path=root/'Tools/Disasm/Reports/ControlFlow.json';value=json.loads(pending[path]);group=next(r for r in value if r['name']=='Controls')
    group['blocks'].append(dict(slot=23,offset=0x1CB,length=256,origin=0x4000,name='Controls',roots=[0x4000]))
    group['unresolved'].append(dict(address=0x402E,operation='JP #3D13',target=0x3D13,bank=0,reason='внешний TR-DOS, слово внешнего возврата 6300'))
    pending[path]=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
