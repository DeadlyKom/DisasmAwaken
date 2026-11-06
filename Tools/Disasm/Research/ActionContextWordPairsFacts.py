"""Сравнение четырёх слов контекста без сравнения управляющих соседних байтов."""
FUNCTIONS={0x6986:('CompareContextWordPairs','Сравнение двух пар слов контекста с ранним выходом по первой разности')}
LOCAL={};LABELS={};CONTINUATIONS={}
RENAMES={'Action.Unknown6986.Entry':'Action.CompareContextWordPairs.Entry'}
CONTRACTS={('Action',0x6986):(
    ['HL, DE, BC входных аргументов не задают, AF задаёт сохраняемый A',
     'SeedFirst и SeedSecond текущего контекста, OtherFirst и OtherSecond доступны для чтения',
     'перенесённый ACTION доступен, на CPU-стеке внешний возврат, IRQ не вмешиваются'],
    ['если SeedFirst не равен OtherFirst, HL=SeedFirst-OtherFirst по модулю слова, DE=OtherFirst',
     'иначе HL=SeedSecond-OtherSecond по модулю слова, DE=OtherSecond',
     'BC и A сохраняются, F соответствует последнему 16-битному вычитанию с исходным Carry=0',
     'Z установлен тогда и только тогда, когда обе пары слов равны, соседние управляющие байты не сравниваются',
     "HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и страница сохраняются",
     'RAM и CPU-стек не записываются, R получает 7 M1 для первой разности либо 14 для второго сравнения, бит 7 сохранён'],
    ['HL, DE, F, R'],
    ['перед каждым SBC Carry очищается через OR A, разность первой пары не передаётся во вторую',
     'это проверка равенства двух слов в каждом контексте, полного равенства пятибайтовых контекстов она не доказывает',
     '663552 сценария проверили все первые и вторые слова при четырёх границах другой стороны, все входные AF и смешанные слова',
     'сопоставлены регистры включая R, отсутствие записей каждого сценария и итоговое совпадение восьми банков RAM',
     'полное произведение четырёх слов, игровые роли второго контекста, IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
0x6986:(['Чтение первой пары слов, первая разность определяет ранний выход.'],None),
0x698D:(['Расчёт разности первых слов с очищенным Carry, входной A не изменяется.'],None),
0x6990:([], 'выход, если SeedFirst отличается от OtherFirst, вернуть первую разность'),
0x6991:(['Чтение второй пары только после равенства первой.'],None),
0x6998:(['Расчёт независимой разности вторых слов без переноса предыдущего сравнения.'],None)}


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x6986):return operation
    for value,name in ((0x9BC1,'ControlsParameterTablesState.SeedFirst'),(0x9BC3,'ControlsParameterTablesState.SeedSecond'),
                       (0x9BC6,'ActionContextWordPairsState.OtherFirst'),(0x9BC8,'ActionContextWordPairsState.OtherSecond')):
        operation=operation.replace('#'+format(value,'04X'),'@'+name)
    return operation
