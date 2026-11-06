"""Сумматор четырёх фаз и развёрнутый перенос до передачи управления PresentLookupTexture."""
CONTRACTS={('Intro',0x6B9C):(
    ['четыре младших фазовых индекса подготовлены в операндах 6BA2, 6BA6, 6BA9 и 6BAC',
     '9400..97FF содержат четыре таблицы выборок, 9800..98FF содержит таблицу результата по сумме modulo 256',
     'цепочка 9900..A7FF создана из 256 PhaseSum, предпоследний байт заменён RET, последний EXX недостижим',
     'цепочка A800..ACC2 содержит 304 пары POP HL и LD (nn),HL и завершающий JP PresentLookupTexture',
     'PointerRow по 6BB2 содержит читаемый адрес 608 байтов, штатно F000+16*индекс, индекс 39..71',
     '9300..93FF и первые 16 байтов страниц C0..E5 доступны для записи в текущем банке, источники не повреждаются назначениями',
     'SP - внешний CPU-стек с двумя доступными байтами ниже него, SavedSP доступен для записи, IRQ не вмешивается'],
    ['PC=6BBC перед первой инструкцией PresentLookupTexture, SP=PointerRow+608, CPU SP ещё не восстановлен',
     'HL - последнее прочитанное слово 608-байтового блока, DE=93FF, BC - B=98, C последняя сумма четырёх фаз',
     'A - последний результат таблицы 98, F от INC младшего индекса первой таблицы, Carry от последнего сложения четвёртой выборки',
     "HL'=9600+исходная третья фаза, DE'=9700+исходная четвёртая фаза, BC'=9500+исходная вторая фаза",
     "AF', IX и IY, I/IM/IFF и paging сохраняются, SavedSP содержит входной CPU SP",
     '9300..93FF содержит 256 результатов, 608 байтов блока перенесены по 16 байтов в начала 38 страниц C0..E5',
     'два байта ниже входного CPU SP содержат возврат 6BB1 от завершённого вызова сумматора'],
    ["HL, DE, BC, AF, HL', DE', BC', SP как временный курсор, SavedSP, 256 байтов таблицы, 608 байтов назначения и два байта ниже CPU SP"],
    ['индексы всех фаз увеличиваются младшими байтами без переноса в старшую страницу, полный проход возвращает каждую исходную фазу',
     'EX DE,HL меняет порядок второй и третьей выборок на соседних копиях, сумма modulo 256 сохраняется, флаг последнего сложения относится к первой таблице 94',
     'последний RET сумматора выполняется до INC E и EXX, поэтому E результата равен FF и активен набор таблицы 94',
     'при временном SP перенос не вызывает подпрограмм, завершение идёт через JP, восстановление CPU SP выполняет следующий фрагмент',
     '768 сценариев покрыли все младшие значения каждой фазы в сочетаниях и три CPU-стека, реальные цепочки, регистры кроме R, все банки RAM и кратность записей',
     'все 256 в четвёртой степени сочетаний фаз, продолжение с IRQ, время и нативный показ не доказаны'])}
COMMENTS={
0x6B9C:(['-----------------------------------------','Контексты четырёх фаз','Подготовка таблицы 93 и первого фазового указателя до обмена регистровыми наборами.'],None),
0x6BA4:(['Подготовка трёх остальных фаз после EXX, младшие байты этих операндов меняет AdvanceTexturePhases.'],None),
0x6BAE:(['Создание 256 байтов таблицы 93 настоящей цепочкой суммирования, последний RET оставляет наборы обменёнными.'],None),
0x6BB1:(['-----------------------------------------','Стек данных и перенос слов','Чтение адреса строки из подготовленного операнда PointerRow, исходное слово 2121 является только первоначальными байтами.'],None),
0x6BB4:(['Сохранение внешнего CPU SP в операнде следующего фрагмента перед переключением на блок 608 байтов.'],None),
0x6BB9:(['Передача управления цепочке POP и LD, она завершится JP PresentLookupTexture с ещё временным SP.'],None)}


def name_operands(region,address,operation):
    if (region,address)!=('Intro',0x6B9C):return operation
    for before,after in (('LD DE, #9300','LD DE, @IntroLookupConst.LookupBase'),
        ('LD B, #98','LD B, @IntroLookupConst.ResultPage'),('LD HL, #9400','LD HL, @IntroLookupConst.FirstPhase'),
        ('LD BC, #9500','LD BC, @IntroLookupConst.SecondPhase'),('LD HL, #9600','LD HL, @IntroLookupConst.ThirdPhase'),
        ('LD DE, #9700','LD DE, @IntroLookupConst.FourthPhase'),('CALL #9900','CALL @IntroLookupConst.SumChain'),
        ('JP #A800','JP @IntroLookupConst.CopyChain'),('(#6BBD)','(@IntroLookupState.SavedSP)')):
        operation=operation.replace(before,after)
    return operation


variables='\n                module IntroLookupState\n'
variables+=('SavedSP'.ljust(16)+'equ #6BBD').ljust(80)+'; исходный операнд LD SP,nn в PresentLookupTexture\n'
variables+='                endmodule\n'
constants='\n                module IntroLookupConst\n'
for name,value,note in (('LookupBase',0x9300,'таблица 256 результатов суммы четырёх фаз'),
    ('ResultPage',0x98,'старший байт таблицы результата по сумме'),('FirstPhase',0x9400,'первая таблица выборок'),
    ('SecondPhase',0x9500,'вторая таблица выборок'),('ThirdPhase',0x9600,'третья таблица выборок'),
    ('FourthPhase',0x9700,'четвёртая таблица выборок'),('SumChain',0x9900,'256 созданных копий PhaseSum'),
    ('CopyChain',0xA800,'304 пары POP HL и LD (nn),HL с завершающим JP')):
    constants+=(name.ljust(16)+'equ #'+format(value,'04X' if value>255 else '02X')).ljust(80)+'; '+note+'\n'
constants+='                endmodule\n'
INCLUDE_BLOCKS=(('Includes/Variables/Include.inc','module IntroLookupState',variables),
    ('Includes/Const/Include.inc','module IntroLookupConst',constants))
