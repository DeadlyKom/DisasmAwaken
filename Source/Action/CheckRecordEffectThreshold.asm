                module Action
                module CheckRecordEffectThreshold
                ; Документация [алгоритм и проверка](../../Docs/ActionRecordEffectResume.md)
                ; -----------------------------------------
                ; Выбор порога запуска большого эффекта для текущей записи
                ; исходная запись 17, код ACTION банка 0, смещения #9792..#97BE
                ; In:
                ;   IX указывает текущую запись, читаются LinkedIndex, LinkFlags, Unknown13 и два байта по #9C1A и #9C1B
                ; Out:
                ;   C выбирает порог #0A, #1E, #3C или #14
                ;   при Unknown13 не меньше порога управление передано F7E6 с AF от SUB
                ;   иначе вызывается PrepareLargeEffect и затем исполняется ResumeAfterRecordEffect
                ; Corrupt:
                ;   BC, AF до сравнения, после вызова действует договор обработки эффекта
                ; Note:
                ;   прямой переход F7E6 сохраняет SP, путь эффекта восстанавливает SP перед продолжением
                ; -----------------------------------------
                ; Проверка индекса связи перед выбором повышенного порога.
Entry:          LD A, (IX + @FActionRecord.LinkedIndex)
                CP #1A
                LD C, #0A
                JR NZ, @Action.CheckRecordEffectThreshold.CompareValue          ; переход, если индекс связи отличается от #1A, использовать #0A

                LD C, #0A
                ; Проверка бита 3 LinkFlags.
                BIT 3, (IX + @FActionRecord.LinkFlags)
                JR Z, @Action.CheckRecordEffectThreshold.CompareValue           ; переход, если бит 3 LinkFlags сброшен, использовать #0A

                ; Проверка первого и второго байтов выбора порога.
                LD A, (#9C1A)
                INC A
                LD C, #1E
                JR NZ, @Action.CheckRecordEffectThreshold.CompareValue          ; переход, если первый байт отличается от #FF, использовать #1E

                LD A, (#9C1B)
                INC A
                LD C, #3C
                JR NZ, @Action.CheckRecordEffectThreshold.CompareValue          ; переход, если второй байт отличается от #FF, использовать #3C

                LD C, #14
                ; Сравнение байта записи с выбранным порогом.
CompareValue:   LD A, (IX + @FActionRecord.Unknown13)
                SUB C
                JP NC, @Action.DispatchObjectState.StoreRemainder               ; переход, если байт не меньше порога, продолжить диспетчеризацию

                CALL @Action.PrepareLargeEffect.Entry
                ; JP @Action.ResumeAfterRecordEffect.Entry, продолжение в ResumeAfterRecordEffect.asm

                endmodule
                endmodule
