                module Action
                module PrepareLargeEffect
                ; Документация [алгоритм и проверка](../../Docs/ActionLargeEffectEntry.md)
                ; -----------------------------------------
                ; Настройка дочернего кода и чтение заголовка большого эффекта
                ; исходная запись 17, код ACTION банка 0, смещения #8A29..#8A3C
                ; In:
                ;   IX указывает исходную запись, ClassCode и байтовое смещение модели доступны
                ;   страница 4 содержит OBJECT3D, выбор страниц разрешён, SP в общей RAM, IRQ не вмешиваются
                ; Out:
                ;   ChildMask равна #40 для класса 8 и #A0 для остальных
                ;   HL получает исходный заголовок из OBJECT3D, IX и SP сохранены
                ;   в 7FFD выданы #14 и #10, исполнение продолжается в AllocateLargeEffect
                ; Corrupt:
                ;   HL, AF, R, ChildMask, регистр страницы и временные слова стека
                ; Note:
                ;   проверены все классы и все исходные чётные индексы модели
                ;   смысл продолжения и границы проверки его выделения описаны отдельно
                ; -----------------------------------------
                ; Проверка класса для выбора ChildMask.
Entry:          LD A, (IX + @FActionRecord.ClassCode)
                CP #08
                LD A, #A0
                JR NZ, @Action.PrepareLargeEffect.StoreChildMask                ; переход, если класс отличается от 8, оставить #A0

                LD A, #40
StoreChildMask: LD (@ActionLargeEffectContinuationState.ChildMask), A
                ; Чтение заголовка из страницы OBJECT3D.
                LD A, (IX + @FActionRecord.Unknown06)
                CALL @Action.ReadObjectHeaderWord.Entry
                ; JP @Action.AllocateLargeEffect.Entry, продолжение в AllocateLargeEffect.asm

                endmodule
                endmodule
