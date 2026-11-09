"""7176, настоящий текст, два исходных ожидания и перенос 99 байтов в 4200."""
TAG='ActionHyperJumpPreparation'
TITLE='подготовка копируемого загрузчика гиперперехода'
CASES=2
FUNCTIONS={0x7176:('PrepareHyperJumpRelay','Сообщение гиперперехода, вывод очереди, исходная задержка и перенос загрузчика ACTION в 4200')}
ENDS={0x7176:0x71CB}
KEYS={}
LOCAL={0x7185:'ConsumeLoop',0x7198:'LongDelay',0x719A:'DelayOuter',0x719D:'DelayMiddle',0x719F:'DelayInner'}
MUTATIONS=()
CONTRACTS={('Action',0x7176):(
 ['HL, DE, BC и AF числовых аргументов не задают, пятибайтовый контекст уже скопирован RequestHyperJump',
  'Controls банка 1 содержит QueueTextItem, ConsumeTextQueue и шрифт, текстовое окно предварительно инициализировано',
  'Recognition.Value=FF выбирает длинную задержку, любой другой код короткую, paging разблокирован и исходно выбран банк 0',
  'исходные 99 байтов 71CB..722D доступны для чтения, 4200..4262 и атрибуты 5800..5AFF доступны для записи',
  'обычный стек и стек прокрутки соответствуют договору ConsumeTextQueue, IRQ в проверке отсутствуют'],
 ['сообщение F37F передаётся через QueueTextItemBank1 с сохранением DE, затем выбирается банк 1',
  'ConsumeTextQueue вызывается ровно 256 раз с сохранением BC каждого вызова, текст, очередь и прокрутка меняются по его договору',
  'Recognition.Value, отличный от FF, даёт 64 внешних ожидания, FF даёт 128, каждое содержит 255 на 255 исходных DJNZ',
  'OUT 7FFD получает 1F, выбран банк 7, теневой экран и ROM 1, paging не блокируется',
  '768 байтов базовых атрибутов 5800..5AFF обнуляются перекрывающимся LDIR',
  '99 исходных байтов 71CB..722D переносятся в 4200..4262 и выполняется JP 4200',
  'на границе 4200 HL=722E, DE=4263, BC=0, A=1F, IX, IY, I, IM и IFF сохранены, SP равен входному',
  'альтернативные регистры и Carry определены настоящими текстовыми детьми, F после последнего LDIR равен 60 OR Carry',
  'обычного возврата нет, следующий вход относится к копии загрузчика, его код и ключ ACTION занимают 90 и 9 байтов'],
 ['HL, DE, BC, AF, DE\', BC\', AF\', R, очередь, курсоры и экран текста, базовые атрибуты, 99 байтов копии, paging и временные стеки'],
 ['подготовитель сам не выполняет DI, первый DI находится уже в перенесённом загрузчике',
  'два сквозных профиля исполняют настоящее сообщение, 256 потребителей, 4161600 либо 8323200 DJNZ без подмены счётчиков',
  'сверены восемь банков RAM кроме 64 байтов обычного стека и двух байтов SavedSP прокрутки, основные конечные пары и сохранённые IX/IY/SP/I/IM/IFF',
  'точные регистры текстовых детей, R, такты и общая кратность записей этой серией не доказываются',
  'граница проверки находится перед первой инструкцией копии 4200, TR-DOS, сборка и нативная игра не исполнялись'])}
COMMENTS={
 0x7176:(['Постановка исходного сообщения о разогреве реактора с сохранением DE контекста.'],None),
 0x717E:(['Выбор банка 1 для настоящего потребителя текстового окна.'],None),
 0x7183:(['Подготовка 256 вызовов потребителя, начальный B=0 оборачивается через FF.'],None),
 0x7185:(['Сохранение внешнего BC вокруг текстового ребёнка, внутренний повтор по CR не является новым вызовом цикла.'],None),
 0x718C:(['Проверка Recognition.Value, только полный код FF удваивает число внешних ожиданий.'],None),
 0x7190:([],'переход, если Recognition.Value равен FF, выбрать 128 внешних ожиданий'),
 0x7193:(['Выбор 64 внешних ожиданий для остальных значений Recognition.Value.'],None),
 0x7198:(['Выбор 128 внешних ожиданий при Recognition.Value=FF.'],None),
 0x719A:(['Сохранение внешнего счётчика на время двух вложенных исходных байтовых ожиданий.'],None),
 0x71A2:([],'переход, если средний счётчик A ненулевой, повторить 255 внутренних DJNZ'),
 0x71A7:([],'переход, если внешний счётчик A ненулевой, повторить полное ожидание'),
 0x71AA:(['Выбор банка 7 и теневого экрана перед очисткой базовых атрибутов и переносом загрузчика.'],None),
 0x71B1:(['Очистка 768 базовых атрибутов исходным перекрывающимся LDIR.'],None),
 0x71BD:(['Копирование 90 байтов кода и девятибайтового ключа ACTION в существующее окно 4200.'],None),
 0x71C8:(['Передача в копию загрузчика по 4200, исходный блок по 71CB не является местом исполнения этой стадии.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0x7176):return operation
    replacements={'CALL #6040':'CALL @Action.QueueTextItemBank1.Entry',
      'CALL #AB1B':'CALL @Action.SelectMemoryPage.Entry',
      'CALL #ECA2':'CALL @Controls.ConsumeTextQueue.Entry',
      '(#9C2A)':'(@ActionShipEquipment.Recognition.Value)',
      'LD BC, #7FFD':'LD BC, @Hardware.PagingPort',
      'LD HL, #71CB':'LD HL, @ActionHyperReloadConst.CodeSource',
      'LD BC, #0063':'LD BC, @ActionHyperReloadConst.CopyLength',
      'JP #4200':'JP @Action.ReloadActionAfterHyperJump.Entry'}
    for address,name in LOCAL.items():replacements['#'+format(address,'04X')]='@Action.PrepareHyperJumpRelay.'+name
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    path=root/'Source/Files/17_ACTION.inc';text=pending[path].decode('utf-8')
    for index,name in enumerate(('RequestHyperJump','PrepareHyperJumpRelay')):
        needle='                include "../Action/'+name+'.asm"';assert text.count(needle)==1
        text=text.replace(needle,needle.ljust(80)+'; ('+str(index)+') жёсткий порядок, последовательное исполнение')
    pending[path]=text.encode('utf-8')
