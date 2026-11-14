"""Полная цепь выбора опоры и её физические продолжения, один общий числовой договор."""
from types import SimpleNamespace

FUNCTIONS={
0xF51E:('UpdatePreferredClass18','Выбор опоры по R и потоку 2 либо по приоритету классов с обновлением класса 18'),
0xF527:('CheckPreferredRandomWord','Проверка младшего слова потока 2 и внешнего байта для выбора отдельного кода 26'),
0xF535:('FindPreferredClass0','Поиск опорного класса 0 с продолжением к классам 7 и 5 при отсутствии'),
0xF53F:('ContinuePreferredClass0','Передача выбранного индекса класса 0 в общую проверку класса 18'),
0xF541:('FindPreferredClass7','Поиск опорного класса 7 с продолжением к классу 5 при отсутствии'),
0xF54B:('ContinuePreferredClass7','Передача выбранного индекса класса 7 в общую проверку класса 18'),
0xF54D:('FindPreferredClass5','Поиск последнего опорного класса 5 либо переход к сбросу баз'),
0xF557:('ApplyPreferredToClass18','Запись выбранной опоры в первый класс 18 только при отсутствии класса 3')}
CONTINUATIONS={0xF51E:0xF527,0xF535:0xF53F,0xF541:0xF54B,0xF54D:0xF557}
COMMENTS={
0xF51E:(['Чтение R после двух M1 от входа, старший бит сохраняется, распределение не предполагается.'],None),
0xF520:(['Проверка разрешения дополнительного выбора по потоку 2.'],None),
0xF522:([], 'переход, если прочитанный R меньше E6, искать опору по классам 0, 7 и 5'),
0xF524:(['Обновление настоящего Stream2 перед проверкой его нового младшего байта.'],None),
0xF527:(['Проверка младшего байта нового слова, при прямом входе аргумент находится в L.'],None),
0xF52A:([], 'переход, если L не меньше 28, искать опору по классам'),
0xF52C:(['Проверка существующего внешнего байта, его полное игровое назначение ещё не установлено.'],None),
0xF531:(['Подготовка отдельного кода 1A без подмены его найденным индексом.'],None),
0xF533:([], 'переход, если StatusCode не меньше 50, использовать отдельный код 1A'),
0xF535:(['Поиск первого активного класса 0, приоритет не зависит от позиции классов 7 и 5.'],None),
0xF53A:([], 'переход, если класс 0 не найден, проверить класс 7'),
0xF53C:(['Расчёт индекса найденного IY, полученный Z от сдвигов индекса здесь не означает отказ.'],None),
0xF53F:(['Передача готового индекса и его флагов в общий обработчик, дополнительный CALL не создаётся.'],None),
0xF541:(['Поиск первого активного класса 7, если предыдущий приоритет не дал опоры.'],None),
0xF546:([], 'переход, если класс 7 не найден, проверить класс 5'),
0xF548:(['Расчёт индекса найденного IY с сохранением исходного HL.'],None),
0xF54B:(['Передача готового индекса в общую проверку класса 18 без новой рамки возврата.'],None),
0xF54D:(['Поиск первого активного класса 5, последнего в исходной цепи приоритетов.'],None),
0xF552:([], 'переход, если класс 5 не найден, только обнулить три базовых операнда'),
0xF554:(['Расчёт индекса последнего допустимого опорного класса.'],None),
0xF557:(['Сохранение выбранных A и F в альтернативном AF на время поиска классов 3 и 18.'],None),
0xF558:(['Поиск запрещающего активного класса 3.'],None),
0xF55D:([], 'переход, если активный класс 3 найден, не обновлять класс 18'),
0xF55F:(['Поиск первого активного класса 18 после доказанного отсутствия класса 3.'],None),
0xF564:([], 'переход, если класс 18 не найден, только обнулить базовые операнды'),
0xF566:(['Обновление StateCode целевой записи исходным кодом 0B.'],None),
0xF56A:(['Восстановление выбранных A и F, в альтернативном AF остаётся результат поиска класса 18.'],None),
0xF56B:(['Запись выбранного байта опоры в Phase0OrLink и исходного кода 02 в SavedStateCode целевой записи.'],None)}


def operands(region,address,operation):
    if region!='Action' or address not in FUNCTIONS:return operation
    targets={0xEBB8:'Action.NextRandomWord2.Entry',0xE98D:'Action.FindRecordByCode.Entry',
             0xE6BE:'Action.RecordIYToIndex.Entry',0xF572:'Action.ResetRecordUpdateBases.Entry',
             0x9BCD:'ActionPreferredChanceState.StatusCode'}
    targets.update({a:'Action.'+name+'.Entry' for a,(name,_) in FUNCTIONS.items()})
    for value,name in targets.items():operation=operation.replace('#'+format(value,'04X'),'@'+name)
    for value,field in ((0x0A,'StateCode'),(0x0D,'Phase0OrLink'),(0x16,'SavedStateCode')):
        operation=operation.replace('(IY+#'+format(value,'02X')+')','(IY + @FActionRecord.'+field+')')
    values={'#E6':'ActionPreferredRecordConst.RLimit','#28':'ActionPreferredRecordConst.WordLimit',
            '#50':'ActionPreferredRecordConst.GateLimit','#1A':'ActionRandomRecordConst.DefaultCode',
            '#00':'ActionRandomRecordConst.ClassZero','#07':'ActionFilterClassConst.Class7',
            '#05':'ActionFilterClassConst.Class5','#03':'ActionPreferredRecordConst.Class3',
            '#12':'ActionRandomRecordConst.Class18','#0B':'ActionPreferredRecordConst.RecordCode',
            '#02':'ActionClass0Const.RecordCode'}
    for before,after in values.items():operation=operation.replace(before,'@'+after)
    return operation


def contract(entry):
    inputs=['HL задаёт L нового слова только для CheckPreferredRandomWord, DE задаёт сохраняемый E, BC не задаёт аргумента',
            'AF задаёт выбранный байт опоры для ApplyPreferredToClass18 и двух ContinuePreferred, его F также сохраняется через обмен AF',
            'ACTION банка 0 доступен, действуют договоры FindRecordByCode, RecordIYToIndex и ResetRecordUpdateBases',
            'исходное непосредственное слово LD HL,nn по F573 равно нулю, три Base доступны для записи',
            'достижимы подходящие активные записи либо маркер, CPU-стек не пересекает список, код и состояния, шесть дополнительных байтов доступны',
            'только основной вход может вызвать NextRandomWord2, Stream2 доступен для записи, IRQ не вмешиваются']
    outputs=['HL=0, E сохраняется, BC=FActionRecord, D задаёт последний искавшийся класс, IY последнюю найденную запись либо маркер',
             'Base0, Base1 и Base2 равны нулю при каждом возврате, записи выполняются в исходном порядке',
             'если опора выбрана, класс 3 отсутствует и класс 18 найден, его StateCode=0B, Phase0OrLink=выбранный A, SavedStateCode=02',
             'остальные записи списка не изменяются, при запрете либо отсутствии цели эти три записи не выполняются',
             'AF и альтернативный AF зависят от пути обмена и последнего поиска, точные случаи приведены в документации',
             "HL', DE', BC' сохраняются без вызова генератора, иначе содержат результат Stream2, IX сохраняется",
             'SP=входной SP+2, I, IM, IFF и страница сохраняются, точный R доказан числовой моделью, бит 7 сохранён']
    notes=['каждый физический фрагмент наследует обычный внешний возврат, отдельная инструкция CALL между продолжениями не добавляется',
           'приоритет 0, затем 7, затем 5 выбирает первый экземпляр соответствующего класса, а не первую запись любого из трёх классов',
           'отдельный код 26 допускается только после R>=E6, нового L<28 и StatusCode>=50',
           'после выбора наличие первого активного класса 3 блокирует обновление, изменяется только первый активный класс 18',
           '383744 сценария исполнили все восемь входов и настоящих детей, сопоставлены регистры включая R, восемь банков RAM и кратность записей',
           'полные игровые роли StatusCode, StateCode, Phase0OrLink и SavedStateCode, полный домен состояний и списков, распределение, период, IRQ, точные T, сборка и нативный запуск не доказаны']
    return inputs,outputs,["HL, D, BC, AF, HL', DE', BC', AF', IY, R, три Base, Stream2 при вызове и поля первого класса 18 при разрешённом обновлении, шесть байтов CPU-стека"],notes


BLOCK='\n                ; Пороги и числовые классы исходного выбора опоры F51E\n                module ActionPreferredRecordConst\n'
for name,value,note in (('RLimit',0xE6,'граница чтения R для дополнительного выбора'),('WordLimit',0x28,'верхняя исключённая граница нового L'),
                        ('GateLimit',0x50,'нижняя включённая граница StatusCode'),('Class3',3,'класс, запрещающий обновление'),
                        ('RecordCode',11,'код StateCode целевой записи класса 18')):
    BLOCK+=name.ljust(16)+('equ #'+format(value,'02X')).ljust(64)+'; '+note+'\n'
BLOCK+='                endmodule\n\n'


def fragment(entry):
    end=next((a for a in sorted(FUNCTIONS) if a>entry),0xF572)
    return SimpleNamespace(FUNCTIONS={entry:FUNCTIONS[entry]},LOCAL={},CONTRACTS={('Action',entry):contract(entry)},
        COMMENTS={a:v for a,v in COMMENTS.items() if entry<=a<end},name_operands=operands,FALLTHROUGH=entry in (0xF527,0xF557),
        STATE_FIELDS=(('StatusCode',0x9BCD,'исходный внешний байт порога, полный игровой смысл ещё не доказан'),) if entry==0xF527 else (),
        INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionPreferredRecordConst',BLOCK),) if entry==0xF557 else ())
