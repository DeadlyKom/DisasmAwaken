"""90 байтов копии загрузчика по 4200 и её условный успешный хвост."""
TAG='ActionHyperReload'
TITLE='перенесённый загрузчик ACTION после гиперперехода'
CASES=512
FUNCTIONS={0x4200:('ReloadActionAfterHyperJump','Перенесённая стадия сохранения 481 байта, вызова TR-DOS для ACTION и восстановления состояния перед новым загрузчиком')}
ENDS={0x4200:0x425A}
KEYS={}
LOCAL={0x4234:'AfterLoad'}
MUTATIONS=()
LOCATION='копия загрузчика в фиксированном банке 5, исходные байты 71CB..7224'


def file_offset(address):return 0x1408+address-0x4200


CONTRACTS={('Action',0x4200):(
 ['HL, DE, BC и AF числовых аргументов не задают, исходные 99 байтов 71CB..722D скопированы в 4200..4262',
  'состояние 9BBD..9D9D, буфер 4000..41E0 и ключ 425A..4262 доступны, paging разблокирован',
  'TR-DOS Dispatch и системные переменные доступны, для продолжения требуется успешная внешняя загрузка исходного ACTION по 6000',
  'возврат TR-DOS должен сохранить копию, буфер и нужное окружение, отдельная модель успешного возврата задаёт это явно'],
 ['до дискового вызова DI сбрасывает IFF, IM получает 1, I=3F, IY=5C3A, paging=18, SP заменяется на 5000',
  'ровно 481 байт состояния копируется из 9BBD в 4000, девять байтов ACTION с типом C копируются в 5CDD, 5CF9 получает 0',
  'CALL TrDos.Dispatch по 3D13 получает C=0E, на границе вызова HL=4263, DE=5CE6, BC=000E, AF=0044, SP=4FFE',
  'по 4FFE лежит слово возврата 4234, старый стек клавиатурного диспетчера отброшен',
  'AfterLoad выполняется только как внешнее продолжение после дискового вызова, сам код не проверяет Carry либо код ошибки TR-DOS',
  'на этом пути DI повторяется, ровно 481 байт возвращается из 4000 в 9BBD, последние 31 байт более широкого 512-байтового блока не восстанавливаются',
  'SP получает 5FFF, байты 9B79, 9B7A, 9B7C и 9B7F получают FF,05,FF,00, затем JP ведёт в свежий ActionBoot.RelocateBootstrap по 6000',
  'на конечной границе HL=41E1, DE=9D9E, BC=0, AF=0044, IFF=0, IX и IY сохраняют возвращённые TR-DOS значения',
  'I, IM, альтернативные регистры и paging после дискового вызова не устанавливаются повторно и зависят от внешнего возврата'],
 ['HL, DE, BC, AF, IY до TR-DOS, SP, I, IM, IFF, R, 481 байт буфера и состояния, ключ запроса, системный байт диска, четыре байта состояния и paging до вызова, прочие эффекты внешнего TR-DOS'],
 ['адрес 6000 здесь относится к свежезагруженному ACTION, это не QueueNumberBank1 перенесённого ядра',
  'исходная длина сохранения равна 01E1, она не расширена до 0200 по аналогии с другими переходами',
  '512 сценариев состоят из 256 проверок до настоящей границы TR-DOS и 256 условных успешных возвратов с явно подставленным дисковым ACTION',
  'сверены все банки RAM и кратность записей, основные и сохраняемые регистры, SP, I, IM и IFF, полные R и такты не проверялись',
  'дисковая служба, ошибочный возврат, сборка, IRQ и нативная игра не исполнялись'])}
COMMENTS={
 0x4200:(['Запрет прерываний перед заменой режима и обычного CPU-стека, старой рамке возврат не предусмотрен.'],None),
 0x420B:(['Выбор банка 0 с теневым экраном перед обращением к TR-DOS.'],None),
 0x4212:(['Сохранение ровно 481 байта текущего состояния в существующий буфер 4000.'],None),
 0x4220:(['Копирование физического девятибайтового ключа ACTION с типом C в системный ключ TR-DOS.'],None),
 0x422B:(['Выбор нулевого диска, байт 5CF9 обнуляется до вызова файловой службы.'],None),
 0x422F:(['Запрос файловой операции 0E, после CALL код ошибки и Carry исходно не проверяются.'],None),
 0x4234:(['Внешнее продолжение после TR-DOS, успешная загрузка ACTION по 6000 является отдельным условием.'],None),
 0x4235:(['Восстановление 481 байта сохранённого состояния, оставшиеся 31 байт 512-байтовой области не копируются.'],None),
 0x4240:(['Замена CPU-стека и обновление четырёх существующих байтов перед новым загрузчиком.'],None),
 0x4256:(['Повторный запрет прерываний и передача в исходный загрузчик свежезагруженного ACTION.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0x4200):return operation
    replacements={'CALL #3D13':'CALL @TrDos.Dispatch','JP #6000':'JP @ActionBoot.RelocateBootstrap.Entry',
      'LD BC, #7FFD':'LD BC, @Hardware.PagingPort',
      'LD BC, #01E1':'LD BC, @ActionHyperReloadConst.StateLength',
      'LD BC, #0009':'LD BC, @FTrDosFileKey',
      'LD HL, #425A':'LD HL, @ActionHyperReloadFileKey.Action.Name'}
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    import json
    path=root/'Includes/Const/Include.inc';text=path.read_text('utf-8')
    block='                ; Длины исходного копируемого загрузчика гиперперехода\n                module ActionHyperReloadConst\n'
    for name,value,note in (('StateLength',0x1E1,'ровно 481 байт сохранения и восстановления'),
      ('CodeSource',0x71CB,'исходный адрес в перенесённом ядре до копирования'),('CopyLength',99,'90 байтов кода и девять байтов ключа')):
        block+=(name.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+note+'\n'
    block+='                endmodule\n\n';pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=root/'Tools/Disasm/Research/Analyze.py';text=path.read_text('utf-8');needle='BLOCKS = [\n';assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+'    # Доказанная копия 99 байтов по LDIR 71BD, включает девятибайтовый ключ.\n    block(17, 0x1408, 0x63, 0x4200, "Action", (0x4200,)),\n').encode('utf-8')
    path=root/'Tools/Disasm/Reports/ControlFlow.json';value=json.loads(pending[path]);group=next(r for r in value if r['name']=='Action')
    group['blocks'].append(dict(slot=17,offset=0x1408,length=99,origin=0x4200,name='Action',roots=[0x4200]))
    group['unresolved']+= [dict(address=0x4231,operation='CALL #3D13',target=0x3D13,bank=0,reason='внешний TR-DOS, успешный возврат задан отдельно'),
      dict(address=0x4257,operation='JP #6000',target=0x6000,bank=0,reason='свежезагруженный ACTION, вход ActionBoot.RelocateBootstrap')]
    pending[path]=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    path=root/'Source/Action/PrepareHyperJumpRelay.asm';text=path.read_text('utf-8')
    text=text.replace('LD HL, #71CB','LD HL, @ActionHyperReloadConst.CodeSource').replace('LD BC, #0063','LD BC, @ActionHyperReloadConst.CopyLength').replace('JP #4200','JP @Action.ReloadActionAfterHyperJump.Entry')
    pending[path]=text.encode('utf-8')
    path=root/'Tools/Disasm/Research/ActionHyperJumpPreparationFacts.py';text=path.read_text('utf-8');needle="'LD BC, #7FFD':'LD BC, @Hardware.PagingPort'";assert text.count(needle)==1
    text=text.replace(needle,needle+",\n      'LD HL, #71CB':'LD HL, @ActionHyperReloadConst.CodeSource',\n      'LD BC, #0063':'LD BC, @ActionHyperReloadConst.CopyLength',\n      'JP #4200':'JP @Action.ReloadActionAfterHyperJump.Entry'")
    pending[path]=text.encode('utf-8')


# Локальный договор отделён от последующего сквозного ROM-профиля и изменения кода.
CONTRACTS['Action',0x4200] = (['HL, DE, BC и AF числовых аргументов не задают, исходные 99 байтов 71CB..722D скопированы в 4200..4262',
  'состояние 9BBD..9D9D, буфер 4000..41E0 и ключ 425A..4262 доступны, paging разблокирован',
  'TR-DOS Dispatch и системные переменные доступны, для продолжения требуется успешная внешняя загрузка исходного ACTION по 6000',
  'возврат TR-DOS должен сохранить копию, буфер и нужное окружение, отдельная модель успешного возврата задаёт это явно'],
 ['до дискового вызова DI сбрасывает IFF, IM получает 1, I=3F, IY=5C3A, paging=18, SP заменяется на 5000',
  'ровно 481 байт состояния копируется из 9BBD в 4000, девять байтов ACTION с типом C копируются в 5CDD, 5CF9 получает 0',
  'CALL TrDos.Dispatch по 3D13 получает C=0E, на границе вызова HL=4263, DE=5CE6, BC=000E, AF=0044, SP=4FFE',
  'по 4FFE лежит слово возврата 4234, старый стек клавиатурного диспетчера отброшен',
  'AfterLoad выполняется только как внешнее продолжение после дискового вызова, сам код не проверяет Carry либо код ошибки TR-DOS',
  'на этом пути DI повторяется, ровно 481 байт возвращается из 4000 в 9BBD, последние 31 байт более широкого 512-байтового блока не '
  'восстанавливаются',
  'SP получает 5FFF, байты 9B79, 9B7A, 9B7C и 9B7F получают FF,05,FF,00, затем JP ведёт в свежий ActionBoot.RelocateBootstrap по 6000',
  'на конечной границе HL=41E1, DE=9D9E, BC=0, AF=0044, IFF=0, IX и IY сохраняют возвращённые TR-DOS значения',
  'I, IM, альтернативные регистры и paging после дискового вызова не устанавливаются повторно и зависят от внешнего возврата'],
 ['HL, DE, BC, AF, IY до TR-DOS, SP, I, IM, IFF, R, 481 байт буфера и состояния, ключ запроса, системный байт диска, четыре байта '
  'состояния и paging до вызова, прочие эффекты внешнего TR-DOS'],
 ['адрес 6000 здесь относится к свежезагруженному ACTION, это не QueueNumberBank1 перенесённого ядра',
  'исходная длина сохранения равна 01E1, она не расширена до 0200 по аналогии с другими переходами',
  '512 сценариев состоят из 256 проверок до настоящей границы TR-DOS и 256 условных успешных возвратов с явно подставленным дисковым '
  'ACTION',
  'сверены все банки RAM и кратность записей, основные и сохраняемые регистры, SP, I, IM и IFF, полные R и такты не проверялись',
  'в отдельном сквозном прогоне ROM загружает ACTION, проверены 481 байт контекста и два последующих кадра',
  '[профиль с дисковым ROM](../../Docs/StationFlightCycle.md#сквозной-прогон-с-rom-tr-dos)',
  'ошибочный возврат дисковой службы, реальный контроллер и нативная игра этими моделями не проверены'])
