                module ArchiveEngine
                module EnableSceneInterrupts
                ; Документация [настройка IM2](../../Docs/ArchiveEngineStartup.md#прерывание)
                ; -----------------------------------------
                ; установка таблицы IM2 и включение кадровых прерываний сцены
                ; In:
                ;   RAM таблицы и переходника доступна для записи
                ; Out:
                ;   HL - адрес обработчика, DE - #5F01, BC - 0, A и I равны #5E
                ;   таблица #5E00..#5F00 заполнена #5F, #5F5F содержит JP на Interrupt
                ; Corrupt:
                ;   HL, DE, BC, AF, I, IM и IFF
                ; -----------------------------------------
                ; заполнение всех 257 байтов, включая второй байт вектора для значения шины #FF
Entry:          DI
                LD HL, @ArchiveEngineConst.VectorAddress
                LD D, H
                LD E, L
                INC DE
                LD (HL), @ArchiveEngineConst.VectorValue
                LD BC, @ArchiveEngineConst.VectorTail
                LDIR

                ; формирование переходника, выбор таблицы и разрешение IRQ после возврата
                LD A, @ArchiveEngineConst.JumpOpcode
                LD (@ArchiveEngineState.VectorJump), A
                LD HL, @ArchiveEngine.Interrupt.Entry
                LD (@ArchiveEngineState.VectorTarget), HL
                LD A, @ArchiveEngineConst.VectorPage
                LD I, A
                IM 2
                EI
                RET

                endmodule
                endmodule
