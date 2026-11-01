"""Полные локальные договоры четырнадцати ранее не выделенных входов эффектов."""
FUNCTIONS={};RANGES={};CONTRACTS={};COMMENTS={};LABELS={}
PRESERVED='индексные регистры, I, IM и IFF сохранены, SP увеличен на два обычным RET'
FIELDS={'PendingDelayA':(0xDE7A,'ожидающая задержка тонального скольжения A'),'PendingStepA':(0xDE82,'ожидающее слово шага тонального скольжения A'),'PendingBranchA':(0xDE88,'ожидаемое смещение JR после обновления тона A'),'PendingTargetA':(0xDE75,'ожидающая целевая нота ограниченного скольжения A'),'PendingNoteA':(0xDE4D,'ожидающая нота строки A'),'CurrentNoteA':(0xE0BB,'текущая нота в сравнении ограниченного скольжения A'),'TargetNoteC':(0xE2B1,'целевая нота ограниченного скольжения C'),'CurrentNoteC':(0xE2B9,'текущий индекс ноты C'),'PreviousNoteC':(0xE6EC,'сохранённая декодером прежняя нота C, изменяемый операнд LD (HL),n')}
TARGETS={a:'MusicEffectState.'+name for name,(a,note) in FIELDS.items()}
TARGETS.update({0xDF08:'MusicChannelBRow.PendingDelay',0xDF10:'MusicChannelBRow.PendingStep',0xDF16:'MusicChannelBRow.PendingBranch',0xDF03:'MusicChannelBRow.PendingTarget',0xDEDB:'MusicChannelBRow.PendingNote',0xE1BB:'MusicChannelBRow.CurrentNote',0xE29D:'MusicState.SlideCounterC',0xE2CC:'MusicState.SlideReloadC',0xE2A6:'MusicState.SlideStepC',0xE2AD:'MusicState.SlideBranchC',0xE2D5:'MusicGateState.CounterC',0xDEA6:'MusicChannelAState.SamplePosition',0xDEA3:'MusicChannelAState.SampleCommand',0xDEB1:'MusicChannelAState.OrnamentPos',0xDEAE:'MusicChannelAState.OrnamentCommand',0xDF34:'MusicChannelBState.SamplePosition',0xDF31:'MusicChannelBState.SampleCommand',0xDF3F:'MusicChannelBState.OrnamentPos',0xDF3C:'MusicChannelBState.OrnamentCommand',0xDF25:'MusicChannelBState.EnabledTicks',0xDF2D:'MusicChannelBState.DisabledTicks',0xDF1E:'MusicChannelBState.GateCommand',0xE1F9:'MusicChannelBRowC.SampleCursor',0xE27A:'MusicChannelBRowC.OrnamentCursor',0xDF62:'MusicEnvelopeState.RowTempo'})
# Имена текущих курсоров C задаются здесь отдельно, до разбора полного синтеза канала.
FIELDS.update({'SampleCursorC':(0xE1F9,'текущая позиция сэмпла C'),'OrnamentCursorC':(0xE27A,'текущая позиция орнамента C')})
TARGETS[0xE1F9]='MusicEffectState.SampleCursorC';TARGETS[0xE27A]='MusicEffectState.OrnamentCursorC'


def add(a,end,name,description,inside,outside,corrupt,notes):
 FUNCTIONS[a]=(name,description);RANGES[a]=end;CONTRACTS['Music',a]=(inside,outside,[corrupt],[*notes,PRESERVED]);COMMENTS[a]=([description],None)


for channel,a,end in (('A',0xE60C,0xE623),('B',0xE65D,0xE674)):
 add(a,end,'SetToneSlide'+channel,'Чтение задержки и шага неограниченного скольжения тона '+channel,
  ['DE указывает на задержку и младший, старший байты шага, F сохраняется',"D' задаёт код включения отложенного блока, штатное значение 06"],
  ['HL=слово шага, DE=входной DE+3, BC сохранён, A=1D, F сохранён',"E' получает D', остальные альтернативные байты сохранены",'ожидающие задержка и шаг обновлены, смещение JR получает 1D для обхода ограничения целевой нотой'],
  "HL, DE, AF только A, DE' только E', ожидающие задержка, шаг и смещение JR, R",
  ['параметры применяются последующим блоком подготовки строки, текущий синтез этой командой не выполняется'])
for channel,a,end,pending in (('A',0xE623,0xE647,0xDE4D),('B',0xE674,0xE698,0xDEDB),('C',0xE6C9,0xE6EE,0xE2B9)):
 shared=['DE указывает на пять байтов, задержка, два пропускаемых байта, младший и старший байты шага',
  'ожидающая нота содержит новую цель, текущая либо сохранённая прежняя нота содержит начало скольжения']
 out=['HL=адрес ожидающей ноты '+format(pending,'04X')+', DE=входной DE+5, B=0, C сохранён, F=44',
  'целевая нота получает новую ожидающую ноту, ожидающая нота заменяется прежней, слово шага обновлено, смещение JR=0']
 if channel=='C':out+=['A=новая целевая нота, задержка записана в текущий счётчик и перезагрузку, счётчик чередования обнулён','альтернативные пары сохранены']
 else:shared+=["D' задаёт код включения отложенного блока, штатное значение 06"];out += ["A=прежняя текущая нота, E' получает D', остальные альтернативные байты сохранены",'задержка и шаг записаны в ожидающие операнды, применяются при подготовке следующей строки']
 add(a,end,'SetTonePortamento'+channel,'Настройка ограниченного скольжения от прежней ноты к новой цели '+channel,shared,out,"HL, DE, BC только B, AF"+("" if channel=='C' else ", DE' только E'")+', параметры скольжения, ожидающая и целевая нота, R',
  ['два промежуточных байта только пропускаются, их значения не участвуют в расчёте',
   'C восстанавливает прежнюю ноту из изменяемого операнда E6EC, заполненного декодером при постановке эффекта в стек' if channel=='C' else 'A и B сохраняют прежнюю ноту из текущего состояния до применения отложенного блока'])
for channel,a,b,end in (('A',0xE647,0xE652,0xE65D),('B',0xE698,0xE6A3,0xE6AE),('C',0xE6EE,0xE6F4,0xE6FA)):
 for entry,finish,kind in ((a,b,'Sample'),(b,end,'Ornament')):
  add(entry,finish,'Set'+kind+'Position'+channel,'Чтение позиции '+('сэмпла' if kind=='Sample' else 'орнамента')+' канала '+channel,
   ['DE указывает на байт позиции, входной F сохраняется'],
   ['HL и BC сохранены, DE=входной DE+1, F сохранён, альтернативные пары сохранены',
    'A=входной байт позиции, текущий курсор обновлён немедленно' if channel=='C' else 'A=06, позиция записана в ожидающий операнд, код отложенной команды=06'],
   'DE, AF только A, позиция '+('текущая' if channel=='C' else 'и код отложенной команды')+', R',
   ['байт позиции копируется без проверки длины сэмпла либо орнамента'])
add(0xDDEA,0xDDEE,'ReadGateTimingB','Чтение двух длительностей чередования канала B',
 ['DE указывает на две длительности, входной F сохраняется'],
 ['HL и BC сохранены, DE=входной DE+2, A=06, F сохранён, альтернативные пары сохранены','EnabledTicks и DisabledTicks обновлены, GateCommand=06'],
 'DE, AF только A, EnabledTicks, DisabledTicks, GateCommand, R',['первый байт читается здесь, JR передаёт управление в SetGateTimingB по DDF2'])
add(0xDDF2,0xDE00,'SetGateTimingB','Установка двух подготовленных длительностей чередования канала B',
 ['DE указывает на вторую длительность, A содержит первую, F сохраняется'],
 ['HL и BC сохранены, DE=входной DE+1, A=06, F сохранён, альтернативные пары сохранены','EnabledTicks получает входную A, DisabledTicks получает байт потока, GateCommand=06'],
 'DE, AF только A, EnabledTicks, DisabledTicks, GateCommand, R',['нулевые длительности сохраняются без нормализации'])
add(0xE6FA,0xE700,'SetRowTempo','Чтение и установка изменяемого темпа музыкальной строки',
 ['DE указывает на байт темпа, входной F сохраняется'],
 ['HL и BC сохранены, DE=входной DE+1, A=байт темпа, F сохранён, альтернативные пары сохранены','RowTempo по DF62 обновлён, текущая Phase по E37D не меняется'],
 'DE, AF только A, RowTempo, R',['новый темп переносится в Phase при следующем проходе StageEnvelopeAndNoise, нулевой темп не исправляется'])
for a,(name,description) in FUNCTIONS.items():TARGETS[a]='Music.'+name+'.Entry'
COMMENTS.update({
 0xE611:(['чтение младшего и старшего байтов шага с продвижением полного указателя потока'],None),
 0xE61A:(['выбор ветви без ограничения целевой нотой для последующего применения шага'],None),
 0xE61F:(['включение отложенного блока скольжения через E\' по коду из D\''],None),
 0xE628:(['пропуск двух промежуточных байтов перед чтением знакового слова шага'],None),
 0xE633:(['выбор ограничения целевой нотой, B обнуляется как признак сохранения прежней основы'],None),
 0xE638:(['сохранение новой целевой ноты и возврат прежней ноты в ожидающий операнд A'],None),
 0xE662:(['чтение младшего и старшего байтов шага B с продвижением полного указателя потока'],None),
 0xE66B:(['выбор ветви без ограничения целевой нотой для последующего применения шага B'],None),
 0xE670:(['включение отложенного блока скольжения B через E\' по коду из D\''],None),
 0xE679:(['пропуск двух промежуточных байтов перед чтением знакового слова шага B'],None),
 0xE684:(['выбор ограничения целевой нотой B и сохранения прежней основы'],None),
 0xE689:(['сохранение новой целевой ноты и возврат прежней ноты в ожидающий операнд B'],None),
 0xE6D1:(['пропуск двух промежуточных байтов перед чтением знакового слова шага C'],None),
 0xE6DC:(['отключение чередования C и выбор пути ограничения целевой нотой'],None),
 0xE6E4:(['сохранение новой цели C перед восстановлением ноты, захваченной декодером'],None),
 0xE6EB:(['восстановление прежней ноты C из изменяемого операнда, подготовленного декодером'],None)})
UNEXTRACTED_TARGETS={0xDE7A:0xDE79,0xDE82:0xDE81,0xDE88:0xDE87,0xDE75:0xDE74,0xE0BB:0xE0BA,0xE1BB:0xE1BA,0xE2B1:0xE2B0,0xE2B9:0xE2B8}


def name_operands(region,address,operation):
 if region!='Music':return operation
 if address in FUNCTIONS:
  import re
  operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
  if operation=='LD A, #06':operation='LD A, @MusicCommandConst.EnableDeferred'
  if operation=='LD A, #1D':operation='LD A, @MusicCommandConst.SkipToneLimit'
 if address==0xE583:operation=operation.replace('(#E6EC)','(@MusicEffectState.PreviousNoteC)')
 return operation
