"""F255, общий создающий вход из координат текущего объекта и его связи."""
FUNCTIONS={0xF255:('SpawnClass17FromCurrentLink','Подготовка компонент и индексов текущей записи для общего создателя класса 17')}
LOCAL={0xF27D:'CreateLinked'}
CONTRACTS={('Action',0xF255):(
    ['HL сохраняется до общего создателя, DE, BC и AF числовых аргументов не задают',
     'IX указывает FActionRecord с Components, LinkedIndex и ReuseByte, запись может иметь любое исходное содержимое',
     'действуют договоры RecordIXToIndex и CreateClass17LinkedRecord, список слотов и обычный целевой индекс LinkedIndex доступны',
     'ACTION банка 0 и перенесённый код банка 5 доступны, шесть дополнительных байтов CPU-стека доступны, IRQ исключены'],
    ['альтернативные HL, DE и BC получают три текущих Components, альтернативный AF перед созданием устанавливается в 0044',
     'B получает обычный индекс текущего IX, C исходный LinkedIndex, будущий Unknown11 ребёнка равен нулю',
     'A для общего создателя равен 0A при сброшенном бите 3 ReuseByte либо 32 при установленном',
     'передача CreateClass17LinkedRecord выполняется настоящим JP без новой возвратной рамки',
     'при успехе ребёнок класса 17 получает State08, Components текущей записи, Unknown0D её индекс и TargetIndex её прежний LinkedIndex',
     'целевая запись получает бит 1 LinkFlags и обратную ссылку на ребёнка, остальные эффекты соответствуют общему создателю',
     "HL, DE, BC, AF и IY определяются результатом создателя, HL'/DE'/BC' содержат скопированные Components, AF'=0044 на всех путях",
     'IX, I/IM/IFF и paging сохраняются, SP после внешнего RET равен входному SP+2, дополнительных OUT нет',
     'R добавляет 42 M1 при сброшенном бите 3 либо 43 при установленном, затем полную стоимость общего создателя'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', IY, R, изменяемый параметр и поля записей из договора создателя, CPU-стек, SP внешним RET"],
    ['бит 3 здесь только выбирает числовой параметр Unknown13, остальные его игровые роли не устанавливаются',
     'исходная LinkFlags текущей записи не проверяется, FF в LinkedIndex передаётся как обычный индекс цели',
     '131072 сценария исполнили все сочетания байтов LinkedIndex, ReuseByte и вариантов поиска с реальным создателем до внешнего RET',
     'проверены точные регистры, флаги, R, восемь банков и кратность записей, компоненты и позиции родителя изменялись по повторяемым формулам',
     'полное произведение входов, аппаратные IRQ, время, сборка и нативная игра не проверялись'])}
COMMENTS={
    0xF255:(['Подготовка обычного индекса цели из текущего LinkedIndex перед переносом компонент.'],None),
    0xF258:(['Копирование трёх Components текущей записи в альтернативный набор для общего создателя.'],None),
    0xF26C:(['Обновление альтернативного A нулём для начального Unknown11, альтернативные флаги становятся 44.'],None),
    0xF26F:(['Расчёт обычного индекса текущего IX для отдельного поля Unknown0D ребёнка.'],None),
    0xF273:(['Проверка бита 3 ReuseByte перед выбором начального Unknown13.'],None),
    0xF279:([],'переход, если бит 3 ReuseByte сброшен, создать запись с параметром 0A'),
    0xF27B:(['Обновление параметра до 32 при установленном бите 3 без изменения самого ReuseByte.'],None),
    0xF27D:(['Создание и обратная связь выполняются общим хвостом без дополнительного CALL.'],None),
}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF255):return operation
    for offset in range(6):
        name='Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')
        operation=operation.replace('(IX+#'+format(offset,'02X')+')','(IX + @FActionRecord.'+name+')')
    return (operation.replace('(IX+#0B)','(IX + @FActionRecord.LinkedIndex)')
            .replace('(IX+#18)','(IX + @FActionRecord.ReuseByte)')
            .replace('CALL #E6B5','CALL @Action.RecordIXToIndex.Entry')
            .replace('JP #60E8','JP @Action.CreateClass17LinkedRecord.Entry')
            .replace('LD A, #0A','LD A, @ActionMissileCreateConst.FallbackParam')
            .replace('LD A, #32','LD A, @ActionMissileCreateConst.PreferredParam'))
