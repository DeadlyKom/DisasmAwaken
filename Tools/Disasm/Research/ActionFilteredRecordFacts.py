"""Общий договор трёх доказанных фильтров, числовые коды классов без придуманного игрового имени."""
from types import SimpleNamespace


def make(entry,name,description,kind):
    first,second=(5,14) if kind=='5or14' else (6,7)
    skip_both=kind=='except'
    contracts={('Action',entry):(
        ['HL сохраняется, DE задаёт сохраняемый D и начальный E, BC и AF аргументов не задают',
         'ACTION банка 0 доступен, поиск начинается с физического Record00 с шагом FActionRecord',
         'достижим подходящий активный элемент либо маркер 80,80, вмешательство IRQ исключено',
         'на CPU-стеке внешний возврат, шесть байтов ниже него доступны настоящему RecordIYToIndex'],
        ['HL и D сохраняются, BC=FActionRecord, IY указывает найденный элемент либо маркер',
         'при находке A равен индексу, E=(ClassCode+1) AND FF, F от INC E с Carry=0 для проверенной области списка',
         'при маркере A=80, F=42, E содержит последний проверенный ClassCode либо входной E при отсутствии активных элементов',
         "HL', DE', BC', AF', IX сохраняются, SP=входной SP+2, I, IM, IFF и страница сохраняются",
         'R определяется числом пропущенных записей и проверок, точная формула приведена в документации'],
        ['E, BC, AF, IY, R и до шести байтов CPU-стека'],
        ['активность определяется NextActiveRecord по байту 1, ClassCode читается только после успешного возврата итератора',
         'предел массива не зашит, отсутствие достижимой находки или маркера не имеет обещания завершения',
         'E увеличивается после получения индекса, при принятом классе FF возвращается Z, такой случай сохраняется в исключающем фильтре',
         '14929 сценариев проверили 256 классов на 26 позициях исследовательского списка, его размер не объявляется игровой ёмкостью',
         'настоящие итератор и преобразование индекса исполнены, сопоставлены все регистры включая R, восемь банков RAM и кратность записей',
         'полное произведение списков, аппаратный порядок записи слов, IRQ, точные T, сборка и нативный запуск не доказаны'])}
    first_note=('проверенный ClassCode равен '+str(first)+', продолжить поиск') if skip_both else ('ClassCode равен '+str(first)+', получить индекс')
    second_note=('ClassCode равен '+str(second)+', продолжить поиск') if skip_both else ('ClassCode отличается от '+str(second)+', продолжить поиск')
    comments={
        entry:(['Выбор позиции перед Record00, NextActiveRecord прибавляет шаг до первого чтения.'],None),
        entry+7:(['Поиск следующей активной записи либо маркера, пропущенные строки не проверяются по ClassCode.'],None),
        entry+10:([], 'выход, если NextActiveRecord вернул маркер конца 80,80'),
        entry+11:(['Чтение полного ClassCode активной записи для двух сравнений.'],None),
        entry+15:(['Проверка первого числового класса фильтра.'],None),
        entry+17:([], 'переход, если '+first_note),
        entry+19:(['Проверка второго числового класса фильтра.'],None),
        entry+21:([], 'переход, если '+second_note),
        entry+23:(['Расчёт байтового индекса найденного IY с сохранением исходного HL.'],None),
        entry+26:(['Формирование результата по ClassCode+1, исходный FF оборачивается в ноль и возвращает Z.'],None)}

    def operands(region,address,operation):
        if (region,address)!=('Action',entry):return operation
        operation=operation.replace('#A0C0','@ActionObjectRecords.Record00-@FActionRecord').replace('#0040','@FActionRecord')
        operation=operation.replace('(IY+#12)','(IY + @FActionRecord.ClassCode)')
        operation=operation.replace('#E6D1','@Action.NextActiveRecord.Entry').replace('#E6BE','@Action.RecordIYToIndex.Entry')
        for value in (first,second):operation=operation.replace('CP #'+format(value,'02X'),'CP @ActionFilterClassConst.Class'+str(value))
        return operation
    block='\n                ; Числовые классы существующих фильтров ACTION\n                module ActionFilterClassConst\n'
    for value in (5,6,7,14):block+=('Class'+str(value)).ljust(16)+('equ #'+format(value,'02X')).ljust(64)+'; исходный числовой код класса '+str(value)+'\n'
    block+='                endmodule\n\n'
    return SimpleNamespace(FUNCTIONS={entry:(name,description)},LOCAL={entry+7:'ScanNext',entry+23:'IndexRecord'},
        CONTRACTS=contracts,COMMENTS=comments,name_operands=operands,
        INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionFilterClassConst',block),) if entry==0xE70D else ())
