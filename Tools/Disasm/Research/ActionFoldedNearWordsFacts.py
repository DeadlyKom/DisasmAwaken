"""Доказанный интервальный предикат верхних слов трёх четырёхбайтовых компонент."""
FUNCTIONS={0x6A29:('CheckThreeUpperWordsNear','Проверка трёх знаковых верхних слов на диапазон от минус 60 до 59')}
LOCAL={0x6A39:'CheckFirst',0x6A50:'CheckSecond',0x6A67:'CheckThird'}
LABELS={('Action',a):name for a,name in LOCAL.items()}
RENAMES={'Action.Unknown6A29.Entry':'Action.CheckThreeUpperWordsNear.Entry'}
RENAMES.update({'Action.Unknown6A29.Point'+format(a,'04X'):'Action.CheckThreeUpperWordsNear.'+name for a,name in LOCAL.items()})
CONTINUATIONS={}
CONTRACTS={('Action',0x6A29):(
    ['HL, DE, BC, AF входных аргументов не задают',
     'IY указывает доступные слова little-endian по смещениям 2, 6, 10, старшие байты по 3, 7, 11',
     'перенесённый ACTION доступен, CPU-стек содержит внешний возврат, IRQ не вмешиваются'],
    ['Carry установлен тогда и только тогда, когда все три слова как signed16 лежат от -60 до 59 включительно',
     'HL содержит последнее проверенное слово, отрицательное слово преобразовано через XOR FFFF без прибавления единицы',
     'DE, BC сохраняются, A равен ненулевому H при раннем отказе по H либо L при сравнении с 60',
     'F задан OR H при отказе по H либо CP 60 при сравнении младшего байта, Z не является признаком успеха',
     "HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и страница сохраняются",
     'RAM и CPU-стек не записываются, R увеличивается по формуле в документации с сохранением бита 7'],
    ['HL, AF, R'],
    ['слова проверяются по порядку, отказ по одному слову не читает следующие компоненты',
     'инверсия даёт -x-1 для отрицательного signed16, поэтому -60 проходит, а +60 не проходит',
     'два младших байта каждой четырёхбайтовой компоненты не читаются, единицы координат и полный смысл списка здесь не установлены',
     '401920 сценариев проверили все значения каждого слова, все входные AF для трёх типов выхода и смешанные слова',
     'сопоставлены регистры включая R, отсутствие записей и восемь банков RAM, полное произведение трёх слов не перебиралось',
     'IRQ, точные T, сборка и нативный запуск не выполнялись'])}
COMMENTS={}
for start,branch,check,ret,compare,retlow,name in (
    (0x6A29,0x6A31,0x6A39,0x6A3B,0x6A3C,0x6A3F,'первого'),
    (0x6A40,0x6A48,0x6A50,0x6A52,0x6A53,0x6A56,'второго'),
    (0x6A57,0x6A5F,0x6A67,0x6A69,0x6A6A,None,'третьего')):
    COMMENTS[start]=(['Чтение '+name+' верхнего слова, два младших байта компоненты не участвуют.'],None)
    COMMENTS[branch-2]=(['Проверка знака слова перед свёрткой отрицательной половины диапазона.'],None)
    COMMENTS[branch]=([], 'переход, если слово неотрицательное, проверить его без инверсии')
    COMMENTS[branch+2]=(['Расчёт -слово-1 инверсией двух байтов, прибавления единицы в оригинале нет.'],None)
    COMMENTS[check]=(['Проверка старшего байта свёрнутого слова, ненулевой байт уже исключает близость.'],None)
    COMMENTS[ret]=([], 'выход, если старший байт ненулевой, вернуть Carry=0')
    COMMENTS[compare]=(['Проверка младшего байта на строгую границу 60.'],None)
    if retlow:COMMENTS[retlow]=([], 'выход, если свёрнутое слово не меньше 60, вернуть Carry=0')
BLOCK='\n                ; Смещения читаемого представления, формат остальных байтов не переопределяется\n                module ActionNearWordsConst\n'
for name,value,note in (('Upper0Low',2,'младший байт первого читаемого слова'),('Upper0High',3,'старший байт первого слова'),
    ('Upper1Low',6,'младший байт второго читаемого слова'),('Upper1High',7,'старший байт второго слова'),
    ('Upper2Low',10,'младший байт третьего читаемого слова'),('Upper2High',11,'старший байт третьего слова'),
    ('SignBit',7,'знаковый бит старшего байта'),('Limit',60,'исключённая верхняя граница свёрнутого слова')):
    BLOCK+=name.ljust(16)+('equ #'+format(value,'02X')).ljust(64)+'; '+note+'\n'
BLOCK+='                endmodule\n\n'


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x6A29):return operation
    for value,name in ((2,'Upper0Low'),(3,'Upper0High'),(6,'Upper1Low'),(7,'Upper1High'),(10,'Upper2Low'),(11,'Upper2High')):
        operation=operation.replace('(IY+#'+format(value,'02X')+')','(IY + @ActionNearWordsConst.'+name+')')
    return operation.replace('BIT 7, H','BIT @ActionNearWordsConst.SignBit, H').replace('CP #3C','CP @ActionNearWordsConst.Limit')
