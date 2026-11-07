                module Action
                module SpawnClass17FromCurrentLink
                ; Документация [алгоритм и проверка](../../Docs/ActionSpawnCurrentLink.md)
                ; -----------------------------------------
                ; Подготовка компонент и индексов текущей записи для общего создателя класса 17
                ; исходная запись 17, адреса F255..F27F
                ; In:
                ;   HL сохраняется до общего создателя, DE, BC и AF числовых аргументов не задают
                ;   IX указывает FActionRecord с Components, LinkedIndex и ReuseByte, запись может иметь любое исходное содержимое
                ;   действуют договоры RecordIXToIndex и CreateClass17LinkedRecord, список слотов и обычный целевой индекс LinkedIndex доступны
                ;   ACTION банка 0 и перенесённый код банка 5 доступны, шесть дополнительных байтов CPU-стека доступны, IRQ исключены
                ; Out:
                ;   альтернативные HL, DE и BC получают три текущих Components, альтернативный AF перед созданием устанавливается в 0044
                ;   B получает обычный индекс текущего IX, C исходный LinkedIndex, будущий Unknown11 ребёнка равен нулю
                ;   A для общего создателя равен 0A при сброшенном бите 3 ReuseByte либо 32 при установленном
                ;   передача CreateClass17LinkedRecord выполняется настоящим JP без новой возвратной рамки
                ;   при успехе ребёнок класса 17 получает State08, Components текущей записи, Unknown0D её индекс и TargetIndex её прежний LinkedIndex
                ;   целевая запись получает бит 1 LinkFlags и обратную ссылку на ребёнка, остальные эффекты соответствуют общему создателю
                ;   HL, DE, BC, AF и IY определяются результатом создателя, HL'/DE'/BC' содержат скопированные Components, AF'=0044 на всех путях
                ;   IX, I/IM/IFF и paging сохраняются, SP после внешнего RET равен входному SP+2, дополнительных OUT нет
                ;   R добавляет 42 M1 при сброшенном бите 3 либо 43 при установленном, затем полную стоимость общего создателя
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, изменяемый параметр и поля записей из договора создателя, CPU-стек, SP внешним RET
                ; Note:
                ;   бит 3 здесь только выбирает числовой параметр Unknown13, остальные его игровые роли не устанавливаются
                ;   исходная LinkFlags текущей записи не проверяется, FF в LinkedIndex передаётся как обычный индекс цели
                ;   131072 сценария исполнили все сочетания байтов LinkedIndex, ReuseByte и вариантов поиска с реальным создателем до внешнего RET
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
                ; Обновление альтернативного A нулём для начального Unknown11, альтернативные флаги становятся 44.
                EX AF, AF'
                XOR A
                EX AF, AF'
                ; Расчёт обычного индекса текущего IX для отдельного поля Unknown0D ребёнка.
                CALL @Action.RecordIXToIndex.Entry
                LD B, A
                ; Проверка бита 3 ReuseByte перед выбором начального Unknown13.
                BIT 3, (IX + @FActionRecord.ReuseByte)
                LD A, @ActionMissileCreateConst.FallbackParam
                JR Z, @Action.SpawnClass17FromCurrentLink.CreateLinked          ; переход, если бит 3 ReuseByte сброшен, создать запись с параметром 0A

                ; Обновление параметра до 32 при установленном бите 3 без изменения самого ReuseByte.
                LD A, @ActionMissileCreateConst.PreferredParam
                ; Создание и обратная связь выполняются общим хвостом без дополнительного CALL.
CreateLinked:   JP @Action.CreateClass17LinkedRecord.Entry

                endmodule
                endmodule
