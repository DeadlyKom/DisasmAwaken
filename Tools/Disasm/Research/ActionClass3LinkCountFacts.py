"""Ограниченный счётчик конъюнкции класса 3, кода 02 и точного байта связи."""
FUNCTIONS={0x62CF:('CountClass3LinksUpToTwo','Подсчёт до двух активных записей класса 3 с кодом 02 и совпадающей ссылкой')}
LOCAL={0x62DA:'CheckEnd',0x62E1:'ScanNext',0x630D:'FinishCount'}
LABELS={('Action',a):name for a,name in LOCAL.items()}
RENAMES={'Action.Unknown62CF.Entry':'Action.CountClass3LinksUpToTwo.Entry'}
RENAMES.update({'Action.Unknown62CF.Point'+format(a,'04X'):'Action.CountClass3LinksUpToTwo.'+name for a,name in LOCAL.items()})
CONTINUATIONS={}
CONTRACTS={('Action',0x62CF):(
    ['HL, DE и AF входных аргументов не задают, BC задаёт сохраняемый начальный C до первой активной строки',
     'IX указывает запись с доступным Unknown0D, сравниваемый байт может иметь любое значение 0..FF',
     'список от Record00 имеет шаг FActionRecord, достижимы два совпадения либо маркер 80,80',
     'читаемые записи и перенесённый код доступны, CPU-стек содержит внешний возврат, IRQ не вмешиваются'],
    ['A=B=число совпадений с насыщением до двух, F=93 для нуля либо одного, F=42 для двух',
     'HL указывает байт 0 маркера при завершении списка либо байт 1 второй подходящей записи',
     'DE=FActionRecord, C содержит младший адрес байта 1 последней активной строки либо входной C, если активных строк не было',
     "HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и страница сохраняются",
     'RAM и CPU-стек не записываются, точная формула R приведена в документации, бит 7 R сохраняется'],
    ['HL, DE, BC, AF, R'],
    ['совпадение требует полного ClassCode=3, полного Unknown0A=02 и LinkedIndex=Unknown0D указанной IX записи',
     'неактивна строка с первым High=80, полный Low=80 при таком High является маркером и прекращает поиск',
     'байт FF в LinkedIndex не является особым отказом, он считается совпадением при Unknown0D=FF',
     'предел массива числом записей не зашит, насыщение прекращает просмотр сразу после второго совпадения',
     '202350 сценариев проверили полные пары классов и кодов, ссылок и целей, двух байтов заголовка и позиции завершения',
     'проверены регистры включая R, отсутствие всех записей и восемь банков RAM, полный набор списков, игровая ёмкость, IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
0x62CF:(['Создание нулевого счётчика и позиции байта High перед первой записью.'],None),
0x62DA:(['Проверка полного Low после найденного High=80, это различает пропуск и маркер конца.'],None),
0x62DE:([], 'переход, если Low также равен 80, закончить подсчёт на маркере'),
0x62E1:(['Поиск следующей записи с исходным шагом FActionRecord.'],None),
0x62E3:(['Проверка активности по полному High, значение 80 не трактуется как отдельный бит.'],None),
0x62E5:([], 'переход, если High равен 80, проверить Low на маркер конца'),
0x62E7:(['Сохранение младшего адреса активного High и переход к полному ClassCode в той же странице.'],None),
0x62ED:(['Проверка класса 3, нулевой и другие классы не учитываются.'],None),
0x62F0:([], 'переход, если ClassCode отличается от 3, продолжить просмотр'),
0x62F2:(['Поиск Unknown0A от адреса High с последующим восстановлением исходного L.'],None),
0x62F7:(['Проверка полного числового кода 02 в Unknown0A.'],None),
0x62FA:([], 'переход, если Unknown0A отличается от 02, продолжить просмотр'),
0x62FC:(['Поиск LinkedIndex для точного сравнения с Unknown0D указанной IX записи.'],None),
0x6301:(['Проверка совпадения полных байтов, FF допускается так же, как любой другой код.'],None),
0x6305:([], 'переход, если LinkedIndex не равен Unknown0D владельца, продолжить просмотр'),
0x6307:(['Обновление счётчика и проверка насыщения на втором совпадении.'],None),
0x630B:([], 'переход, если найдено меньше двух совпадений, продолжить просмотр'),
0x630D:(['Формирование окончательного A и флагов независимо от причины завершения просмотра.'],None)}
BLOCK='\n                ; Граница и маркер исходного счётчика записей класса 3\n                module ActionClass3CountConst\n'
for name,value,note in (('BeforeHigh',0xA0C1,'исходная позиция High перед первым шагом списка, память не выделяется'),
                        ('EndLow',0x80,'полный Low маркера при High=80'),('MaxCount',2,'насыщение счётчика и конечное сравнение')):
    BLOCK+=name.ljust(16)+('equ #'+format(value,'04X' if value>255 else '02X')).ljust(64)+'; '+note+'\n'
BLOCK+='                endmodule\n\n'


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x62CF):return operation
    operation=operation.replace('#A0C1','@ActionClass3CountConst.BeforeHigh').replace('#0040','@FActionRecord')
    operation=operation.replace('(IX+#0D)','(IX + @FActionRecord.Unknown0D)')
    for literal,field in (('#11','ClassCode'),('#09','Unknown0A'),('#0A','LinkedIndex')):
        operation=operation.replace('ADD A, '+literal,'ADD A, @FActionRecord.'+field+'-@FActionWord.High')
    return operation.replace('CP #03','CP @ActionPreferredRecordConst.Class3').replace('CP #80','CP @ActionReuseConst.ReusableHigh').replace('CP #02','CP @ActionClass3CountConst.MaxCount')


def name_instruction(region,function_address,address,operation):
    if (region,function_address)!=('Action',0x62CF):return operation
    if address==0x62DC:return 'CP @ActionClass3CountConst.EndLow'
    if address==0x62F7:return 'CP @ActionClass0Const.RecordCode'
    return operation
