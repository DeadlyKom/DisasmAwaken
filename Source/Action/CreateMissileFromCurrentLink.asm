                module Action
                module CreateMissileFromCurrentLink
                ; Документация [алгоритм и проверка](../../Docs/ActionSpawnCurrentLink.md)
                ; -----------------------------------------
                ; Подготовка компонент и индексов текущей записи для создания связанной ракеты
                ; исходная запись 17, адреса F255..F27F
                ; In:
                ;   HL сохраняется до общего создателя, DE, BC и AF числовых аргументов не задают
                ;   IX указывает FActionRecord с Components, LinkedIndex и ReuseByte, запись может иметь любое исходное содержимое
                ;   действуют договоры RecordIXToIndex и CreateLinkedMissileRecord, список слотов и обычный целевой индекс LinkedIndex доступны
                ;   ACTION банка 0 и перенесённый код банка 5 доступны, шесть дополнительных байтов CPU-стека доступны, IRQ исключены
                ; Out:
                ;   HL при успехе равен 0040, при отсутствии слота сохраняет входное значение
                ;   DE при успехе указывает LinkedIndex цели по первоначальному LinkedIndex текущего IX, при отсутствии слота равен 0040
                ;   BC - B равен RecordIXToIndex текущего IX, C равен исходному LinkedIndex
                ;   AF при успехе содержит A=индекс ребёнка и F=45 OR (A AND 28), при отсутствии слота A=80/F=42
                ;   HL', DE', BC' содержат три Components текущего IX, скопированные до вызова создателя
                ;   AF'=0044 на всех путях
                ;   IX сохраняется, IY указывает ребёнка либо маркер при отказе
                ;   I, IM, IFF и paging сохраняются, SP после внешнего RET равен входному SP+2, дополнительных OUT нет
                ;   R добавляет 42 M1 при сброшенном бите 3 исходного ReuseByte либо 43 при установленном, затем полную стоимость общего создателя
                ;   создателю передаются EffectReserve=0A при сброшенном бите 3 либо 32 при установленном и начальный Unknown11=0
                ;   при успехе ребёнок класса 17 получает State08, скопированные Components, Phase0OrLink=индекс текущего IX, Phase2OrTarget=его первоначальный LinkedIndex
                ;   передача CreateLinkedMissileRecord выполняется настоящим JP без новой возвратной рамки, все эффекты поиска и связывания сохраняются
                ;   цель получает бит 1 LinkFlags и индекс ребёнка в LinkedIndex, при совпадении цели с ребёнком это его конечные LinkFlags=02 и собственный LinkedIndex
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, изменяемый параметр и поля записей из договора создателя, CPU-стек, SP внешним RET
                ; Note:
                ;   нулевой Unknown11 ребёнка является авторским LZS ракеты персонажа, это не всеобщая трактовка поля других классов
                ;   бит 3 здесь только выбирает числовой параметр EffectReserve, остальные его игровые роли не устанавливаются
                ;   исходная LinkFlags текущей записи не проверяется, FF в LinkedIndex передаётся как обычный индекс цели
                ;   131072 сценария исполнили все сочетания байтов LinkedIndex, ReuseByte и вариантов поиска с реальным создателем до внешнего RET
                ;   полное число M1 всех сценариев сверено без потери кратных 128 в R, в 257 случаях совпадения цели и ребёнка отдельно проверены итоговые поля связи
                ;   проверены точные регистры, флаги, R, восемь банков и кратность записей, компоненты и позиции родителя изменялись по повторяемым формулам
                ;   полное произведение входов, аппаратные IRQ, время, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Подготовка обычного индекса цели из текущего LinkedIndex перед переносом компонент.
Entry:          LD C, (IX + @FActionRecord.LinkedIndex)
                ; Копирование трёх Components текущей записи в альтернативный набор для общего создателя.
                EXX
                LD L, (IX + @FActionRecord.Components.Component0.Low)
                LD H, (IX + @FActionRecord.Components.Component0.High)
                LD E, (IX + @FActionRecord.Components.Component1.Low)
                LD D, (IX + @FActionRecord.Components.Component1.High)
                LD C, (IX + @FActionRecord.Components.Component2.Low)
                LD B, (IX + @FActionRecord.Components.Component2.High)
                EXX
                ; Обновление альтернативного A нулём для ракеты персонажа в Unknown11, альтернативные флаги становятся 44.
                EX AF, AF'
                XOR A
                EX AF, AF'
                ; Расчёт обычного индекса текущего IX для отдельного поля Phase0OrLink ребёнка.
                CALL @Action.RecordIXToIndex.Entry
                LD B, A
                ; Проверка бита 3 ReuseByte перед выбором начального EffectReserve.
                BIT 3, (IX + @FActionRecord.ReuseByte)
                LD A, @ActionMissileCreateConst.FallbackParam
                JR Z, @Action.CreateMissileFromCurrentLink.CreateLinked         ; переход, если бит 3 ReuseByte сброшен, создать запись с параметром 0A

                ; Обновление параметра до 32 при установленном бите 3 без изменения самого ReuseByte.
                LD A, @ActionMissileCreateConst.PreferredParam
                ; Создание и обратная связь выполняются общим хвостом без дополнительного CALL.
CreateLinked:   JP @Action.CreateLinkedMissileRecord.Entry

                endmodule
                endmodule
