"""Принудительная перерисовка панели, реальный OUT и хвостовой вывод восьми тетрад."""
FUNCTIONS={0x6145:('RefreshFlightPanel','Принудительное обновление шести шкал и четырёх пар счётчика панели полёта')}
LOCAL={};LABELS={};CONTINUATIONS={}
RENAMES={'Action.Unknown6145.Entry':'Action.RefreshFlightPanel.Entry'}
LOCATION={0x6145:'банк 5, перенесённое ядро ACTION 6000..7F8E'}
CONTRACTS={('Action',0x6145):(
    ['HL, DE, BC и AF числовых аргументов не задают, прежние шесть запросов будут заменены единицами',
     'ActionPanelGaugesState и ActionPreferredByteState задают источники шести шкал, ControlsBcdCounterState задаёт четыре байта счётчика',
     '7FFD не заблокирован, банк 0 содержит ACTION, банк 1 CONTROL и шрифт, экран доступен через общий банк 5',
     'CPU-стек в общей RAM содержит внешний возврат и допускает восемь временных байтов, IRQ не вмешиваются'],
    ['HL содержит LowPairs, DE содержит HighPairs, BC=FF26 после вывода всех восьми знаков',
     'AF соответствует последнему пиксельному OR в старшей тетраде экранного байта 5613',
     "HL'=5613, DE' указывает последнюю строку пары знаков старшей тетрады D, B' содержит сохранённую соседнюю тетраду, C'=F0, AF'=1330",
     'IX, IY, I, IM и IFF сохранены, SP=входной SP+2',
     'перерисованы все шесть шкал и восемь знаков, SecondRequest=1, пять остальных запросов равны нулю',
     'байты счётчика и источники шкал не изменены, после 14 записей в 7FFD итоговая конфигурация равна 11',
     'R увеличен на стоимость обоих рисователей и 29 M1 самой обёртки с двумя вызовами селектора'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', R, экранные байты панели, шесть запросов, восемь байтов CPU-стека и 7FFD"],
    ['хвостовой JP в DrawBcdCounter использует внешний возврат, лишнего CALL и нового слова стека нет',
     'FPanelRefreshGaugeFrame описывает самый глубокий участок вызова шкалы и выбора банка, новая память не выделяется',
     'не-BCD тетрады выводятся как исходные знаки пунктуации, арифметического изменения счётчика нет',
     '6624 сценария композиционной проверки сверяют регистры включая R, восемь физических банков, каждую запись и OUT',
     'исходно заблокированный порт, полное произведение всех полей, IRQ, точные такты, сборка и нативный запуск вне проверки'])}
COMMENTS={
    0x6145:(['Выбор верхнего банка ACTION перед чтением источников шкал, экран остаётся в общем банке 5.'],None),
    0x614A:(['Создание шести запросов в существующих операндах UpdatePanelGauges, старые коды заменяются.'],None),
    0x615E:(['Обновление всех шести шкал, второй запрос сохраняется, остальные потребляются.'],None),
    0x6161:(['Выбор CONTROL и его шрифта для последующего вывода четырёх пар счётчика.'],None),
    0x6166:(['Чтение младших и старших BCD-пар в исходном физическом порядке, счётчик не изменяется.'],None),
    0x616D:(['Разрешение всей цепочки старших пар, значимы только биты 0..2 исходной маски FF.'],None),
    0x616F:(['Хвостовая передача к рисователю цифр, его RET использует уже существующий внешний возврат.'],None)}
CONST_BLOCK=('\n                ; Коды принудительного обновления исходной панели\n                module ActionPanelRefreshConst\n'+
    'RequestAll'.ljust(16)+'equ #01'.ljust(64)+'; записывается в каждый из шести операндов запроса\n'+
    'AllCounterPairs'.ljust(16)+'equ #FF'.ljust(64)+'; биты 0..2 допускают H, E и D по цепочке, биты 7..3 не читаются\n'+
    '                endmodule\n\n')
STRUCT_BLOCK=('\n                ; Самая глубокая динамическая рамка обновления шкалы, память не выделяется\n'+
    '                struct FPanelRefreshGaugeFrame\n'+
    'SavedBC'.ljust(16)+'dw #0000'.ljust(64)+'; сохранённые BC при выборе банка внутри DrawBankedGauge\n'+
    'SelectorRet'.ljust(16)+'dw #0000'.ljust(64)+'; возврат селектора к банковой обёртке шкалы\n'+
    'GaugeRet'.ljust(16)+'dw #0000'.ljust(64)+'; возврат DrawBankedGauge к обработчику одной из шести шкал\n'+
    'PanelRet'.ljust(16)+'dw #6161'.ljust(64)+'; возврат UpdatePanelGauges к выбору банка CONTROL\n'+
    'CallerRet'.ljust(16)+'dw #0000'.ljust(64)+'; исходный возврат, используется после хвостового вывода BCD\n'+
    '                ends\n                assert FPanelRefreshGaugeFrame == #0A\n\n')


def name_operands(region,address,operation):
    if region!='Action' or address not in FUNCTIONS:return operation
    for target,name in ((0x664A,'First'),(0x665C,'Second'),(0x666B,'Third'),(0x667D,'Fourth'),(0x668E,'Fifth'),(0x669F,'Sixth')):
        operation=operation.replace('(#'+format(target,'04X')+')','(@ActionPanelGaugesState.'+name+'Request)')
    return (operation.replace('LD A, #10','LD A, @ActionBankPage.Runtime').replace('LD A, #11','LD A, @ActionBankPage.Controls')
        .replace('LD A, #01','LD A, @ActionPanelRefreshConst.RequestAll').replace('LD B, #FF','LD B, @ActionPanelRefreshConst.AllCounterPairs')
        .replace('(#9BBF)','(@ControlsBcdCounterState.LowPairs)').replace('(#9BBD)','(@ControlsBcdCounterState.HighPairs)')
        .replace('JP #F142','JP @Controls.DrawBcdCounter.Entry'))
