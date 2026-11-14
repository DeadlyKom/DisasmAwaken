                module Final
                module InitializeFinal
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
                ; Документация [банки и цикл финала](../../Docs/FinalCycle.md)
                ; Документация [физические указатели синхронизации](../../Docs/FinalSyncAndPreviewRecord.md)
                ; Документация [Final](../../Docs/FunctionDetails/Final.md)
                ; -----------------------------------------
                ; Подготовка трёх экранных банков, таблицы IM 2 и финальной анимации
                ; исходная запись 29, файловые смещения #0000..#0122
                ; In:
                ;   исходные FINALF и три bitmap доступны, 7FFD разблокирован
                ;   стек в общей RAM, 14 байтов ниже SP свободны и не перекрывают код, исходные bitmap до их копирования, таблицу IM 2 и создаваемую цепочку
                ;   до первой DI прерывания не вмешиваются, после настройки доступен периодический IRQ
                ; Out:
                ;   перед первым BeginFramePair HL=#A937, DE=#8003, BC=0, AF=#019B, I=#BE, IM 2, IFF=0, страница 1 и исходный SP восстановлен
                ;   bitmap распределены по банкам 7, 0 и 1, построены вектор IM 2 и исполняемая цепочка
                ;   каждый проход выполняет два вывода с атрибутами #90 и #A0, между вызовами SP восстановлен
                ;   при дополнительном IRQ в выводе второго кадра возможны записи в растр банка 1 и искажения изображения
                ;   Q и A меняют задержку, Space переводит управление в HaltFinal, обычного RET нет
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, I, IM, IFF, R, стек, таблица IM 2, экран, цепочка, операнды и 7FFD
                ; Note:
                ;   подготовка использует до 14 байтов CPU-стека, стек вне цепочки может всё ещё перекрывать исходные bitmap
                ;   отдельная модель проверила SP=5FFE и 5FFF, при подготовленном SP=7FFE PUSH искажают вторую картинку до её копирования
                ;   три bitmap из #62A9 копируются до перезаписи части исходного файла по #8000
                ;   места #912A и #9EE6 попеременно содержат NOP либо LD SP,#6196 и HALT
                ;   девять сценариев сверили обе картинки, три IRQ за пару выводов, клавиши и выход до HALT
                ;   нулевой операнд задержки даёт 256 проходов цикла, IRQ в задержке использует обычный SP
                ;   при большом значении задержки дополнительный IRQ может использовать SP текущей половины строки
                ; -----------------------------------------
Entry:          LD HL, #5800
                LD DE, #5801
                LD BC, #02FF
                LD (HL), L
                LDIR
                LD A, #1F
                LD BC, #7FFD
                OUT (C), A
                LD HL, #D800
                LD DE, #D801
                LD BC, #02FF
                LD (HL), L
                LDIR
                DI
                LD A, #07
                LD HL, #62A9
                LD BC, #7FFD
                LD DE, #C000
                OUT (C), A
                PUSH DE
                PUSH BC
                LD BC, #1800
                LDIR
                PUSH HL
                LD HL, #D800
                INC DE
                LD BC, #02FF
                LD A, #88
                LD (HL), A
                LDIR
                POP HL
                POP BC
                POP DE
                PUSH DE
                PUSH BC
                LD A, #00
                OUT (C), A
                LD BC, #1800
                LDIR
                POP BC
                POP DE
                LD A, #01
                OUT (C), A
                LD BC, #1800
                LDIR
                LD HL, #BE00
                LD DE, #BE01
                LD A, H
                LD (HL), #BF
                LD I, A
                LD BC, #0100
                LDIR
                LD A, #C3
                LD (#BFBF), A
                LD HL, @Final.Interrupt.Entry
                LD (#BFC0), HL
                IM 2
                CALL @Final.PrepareFrame.Entry
                ; ожидание IRQ перед подготовкой двух мест переключения страницы в создаваемой цепочке
BeginFramePair: EI
                HALT
                EI
                ; Отключение вставки после десятого ряда для первой фазы.
                LD HL, (@FinalSyncPointers.Value.AfterRow10)
                LD (HL), #00
                INC HL
                LD (HL), #00
                INC HL
                LD (HL), #00
                INC HL
                LD (HL), #00
                ; Подготовка остановки до IRQ после восемнадцатого ряда для первой фазы.
                LD HL, (@FinalSyncPointers.Value.AfterRow18)
                LD (HL), #31
                INC HL
                LD DE, @FinalDisplayChainConst.IrqStackTop
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                LD (HL), #76
                LD BC, #7FFD
                LD A, #08
                OUT (C), A
                LD A, #00
                LD (@Final.Interrupt.PagePatch + 1), A
                LD A, #90
                EX AF, AF'
                CALL @FinalDisplayChainConst.GeneratedEntry
                LD BC, #7FFD
                LD A, #01
                OUT (C), A
                LD (@Final.Interrupt.PagePatch + 1), A
                ; Отключение вставки после восемнадцатого ряда для второй фазы.
                LD HL, (@FinalSyncPointers.Value.AfterRow18)
                LD (HL), #00
                INC HL
                LD (HL), #00
                INC HL
                LD (HL), #00
                INC HL
                LD (HL), #00
                ; Подготовка остановки до IRQ после десятого ряда для второй фазы.
                LD HL, (@FinalSyncPointers.Value.AfterRow10)
                LD (HL), #31
                INC HL
                LD DE, @FinalDisplayChainConst.IrqStackTop
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                LD (HL), #76
                LD A, #01
DelaySecond:    NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                DEC A
                JP NZ, @Final.InitializeFinal.DelaySecond                       ; переход, если счётчик задержки после уменьшения ненулевой


                LD A, #A0
                EX AF, AF'
                CALL @FinalDisplayChainConst.GeneratedEntry
                LD A, #00
                OUT (#FE), A
                CALL @Final.ReadSpeedKeys.Entry
                LD A, #7F
                IN A, (#FE)
                RRA
                JP NC, @Final.HaltFinal.Entry                                   ; переход, если нажат Space


                JP @Final.InitializeFinal.BeginFramePair


                endmodule
                endmodule
