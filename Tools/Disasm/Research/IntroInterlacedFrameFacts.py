"""Полное чередование двух половин с настоящим ROM IRQ и точными общими операндами."""
import IntroScatterFacts as scatter

LABELS={('Intro',0x67FF):'StorePatch',('Intro',0x6818):'FirstThenSecond',('Intro',0x6830):'ReadRecord'}
EXPECTED_CONTRACTS={('Intro',0x6827):scatter.CONTRACTS['Intro',0x6827]}
CONTRACTS={('Intro',0x67F1):(
    ['FramePhase - исходный байт фазы 0 либо 80, FirstRecords и SecondRecords содержат по 38 записей указателей и назначений',
     'FirstMatrix и SecondMatrix содержат по 32 слова, писатель 68A9..6928 подготовлен с исходным IXL=80 либо C0',
     'IM=1, IY=5C3A, проверенный 48K ROM, клавиши не нажаты, KSTATE по 5C00 и 5C04 равны FF',
     'входной IFF может быть нулём либо единицей, фаза прихода IRQ влияет на число прерываний до вывода',
     'SP указывает внешний возврат, 16 байтов ниже него доступны, назначения не повреждают код, записи указателей и CPU-стек',
     'источники могут перекрываться с назначениями писателя, порядок чтения и записи должен сохраняться'],
    ['HL - последний адрес источника второй половины плюс один, DE - конец последней строки второй половины после коррекции назначения',
     'BC - входное BC минус 2432 modulo 65536, A=0, F=42 при исходной FramePhase=0 либо 43 при исходной FramePhase=80',
     "HL', DE', BC', AF', IX и IY сохраняются, I и IM сохраняются, IFF=0, SP после RET равен входному SP+2",
     'FramePhase переключён между 0 и 80, AddressPatch равен 00 14 для новой нулевой фазы либо 00 00 для новой 80',
     'выведены две половины по 1216 байтов и 64 байта матрицы между ними, источники читаются из актуальной RAM',
     'для новой фазы 0 порядок SecondRecords, FirstMatrix, FirstRecords, назначения сдвинуты увеличением D на один',
     'для новой фазы 80 порядок FirstRecords, SecondMatrix, SecondRecords без коррекции назначения',
     'RecordCursor указывает за последней записью второй половины, CpuSavedSP содержит входной SP, IntroAttrState.SavedSP содержит входной SP минус два',
     'FRAMES увеличен каждым принятым IRQ, в проверенных начальных состояниях принято одно либо два прерывания'],
    ['HL, DE, BC, AF, R, IFF, FramePhase, общие операнды переноса и писателя, FRAMES, 2496 байтов назначений и 16 временных байтов ниже SP'],
    ['после CALL WaitInterrupt DI запрещает IRQ на время обеих половин и писателя, исходный Carry сложения фазы определяет конечный Carry',
     'при разрешённом входном IFF возможен ранний IRQ до WaitInterrupt, последующий HALT принимает ещё один, число FRAMES нельзя считать всегда равным единице',
     'вторая половина выполняется хвостовым переходом, её RET снимает внешний адрес возврата всего обработчика',
     '1536 комбинаций данных на каждую исходную фазу исполнили настоящий ROM и все дочерние процедуры, всего 3072 сценария',
     'в том числе проверены чтения источников, уже изменённых писателем с адресами 8080..8787',
     'регистры кроме R, все физические банки и кратность записей совпали с числовой композицией',
     'доказаны начальные моменты 0, 100 и 69880 периода 69888, произвольные фазовые байты, времена, ROM, клавиши, NMI и нативный показ не доказаны'])}


def translated(text):
    return text.replace('6839..683A','IntroScatterState.AddressPatch').replace('6831','IntroScatterState.RecordCursor').replace('68A1','IntroScatterState.CpuSavedSP')


CONTRACTS['Intro',0x6827]=tuple([translated(text) for text in section] for section in scatter.CONTRACTS['Intro',0x6827])
COMMENTS={
    0x67F1:(['-----------------------------------------','Две фазы вывода','Чтение собственного операнда FramePhase, штатные значения 0 и 80 чередуются добавлением 80.'],None),
    0x67F3:(['Расчёт новой фазы, Carry равен единице только при исходной фазе 80 и сохраняется дочерними переносами.'],None),
    0x67F5:(['Обновление исходного операнда фазы для следующего вызова.'],None),
    0x67FB:([],'переход, если новая FramePhase равна 80 и коррекция страницы назначения не нужна'),
    0x67FD:(['Создание слова 1400, little-endian запись даст вставку NOP и INC D.'],None),
    0x67FF:(['Обновление двух исходных байтов AddressPatch до ожидания кадрового IRQ.'],None),
    0x6802:(['Ожидание следующего IRQ и запрет дальнейших IRQ перед временными стеками, ROM сохраняет AF проверки фазы.'],None),
    0x6805:([],'переход, если новая FramePhase равна 80 и первой выводится FirstRecords'),
    0x6807:(['-----------------------------------------','Нулевая фаза','Вывод SecondRecords, затем FirstMatrix и хвостовой FirstRecords с коррекцией страницы назначения.'],None),
    0x6818:(['-----------------------------------------','Фаза 80','Вывод FirstRecords, затем SecondMatrix и хвостовой SecondRecords без коррекции назначения.'],None),
    0x6827:(['-----------------------------------------','Общий перенос 38 строк','Сохранение адреса первой четырёхбайтовой записи в изменяемом операнде RecordCursor.'],None),
    0x682A:(['Сохранение CPU SP, после выбора указателей он временно станет стеком слов источников.'],None),
    0x6830:(['Чтение следующей записи через подготовленный RecordCursor, два POP дают адрес списка источников и адрес назначения.'],None),
    0x6835:(['Обновление RecordCursor по SP сразу после прочитанной четырёхбайтовой записи.'],None),
    0x6839:(['Исходная двухбайтовая вставка, рабочие варианты NOP NOP и NOP INC D корректируют только назначение.'],None),
    0x683B:(['Переключение SP на 32 указателя источников, развёрнутые пары POP HL и LDI дают одну строку.'],None),
    0x689C:(['Проверка числа оставшихся строк, исходный Carry фазы сохраняется DEC A.'],None),
    0x689D:([],'переход, если ещё не перенесены все 38 строк'),
    0x68A0:(['Восстановление CpuSavedSP, у хвостовой второй половины он равен внешнему SP всего обработчика.'],None)}


def name_operands(region,address,operation):
    if region!='Intro' or address not in (0x67F1,0x6827):return operation
    for before,after in (('(#67F2)','(@IntroAttrState.FramePhase)'),('(#6839)','(@IntroScatterState.AddressPatch)'),
        ('(#6831)','(@IntroScatterState.RecordCursor)'),('(#68A1)','(@IntroScatterState.CpuSavedSP)'),
        ('LD HL, #6000','LD HL, @IntroFrameConst.FirstRecords'),('LD HL, #6100','LD HL, @IntroFrameConst.SecondRecords'),
        ('LD HL, #60C0','LD HL, @IntroAttrConst.FirstMatrix'),('LD HL, #61C0','LD HL, @IntroAttrConst.SecondMatrix'),
        ('LD H, #14','LD H, @IntroFrameConst.IncrementD')):
        operation=operation.replace(before,after)
    return operation


variables='\n                module IntroScatterState\n'
for name,value,note in (('RecordCursor',0x6831,'операнд LD SP,nn, указатель следующей записи длиной четыре байта'),
    ('CpuSavedSP',0x68A1,'операнд восстановления CPU SP после 38 строк'),
    ('AddressPatch',0x6839,'два исходных NOP, заменяются на 00 00 либо 00 14')):
    variables+=(name.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+note+'\n'
variables+='                endmodule\n'
constants='\n                module IntroFrameConst\n'
for name,value,note in (('FirstRecords',0x6000,'первая таблица 38 записей источника и назначения'),
    ('SecondRecords',0x6100,'вторая таблица 38 записей источника и назначения'),
    ('IncrementD',0x14,'исходный opcode INC D для коррекции страницы назначения')):
    constants+=(name.ljust(16)+'equ #'+format(value,'04X' if value>255 else '02X')).ljust(80)+'; '+note+'\n'
constants+='                endmodule\n'
INCLUDE_BLOCKS=(('Includes/Variables/Include.inc','module IntroScatterState',variables),
    ('Includes/Const/Include.inc','module IntroFrameConst',constants))
