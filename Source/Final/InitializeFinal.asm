                module Final
                module InitializeFinal
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
                ; Документация [банки и цикл финала](../../Docs/FinalCycle.md)
; Документация [Final](../../Docs/FunctionDetails/Final.md)
; -----------------------------------------
; Подготовка трёх экранных банков, таблицы IM 2 и финальной анимации
; исходная запись 29, файловые смещения #0000..#0122
                ; In:
                ;   исходные FINALF и три bitmap доступны, 7FFD разблокирован
                ;   стек в общей RAM вне генерируемой цепочки, доступен периодический IRQ
                ; Out:
                ;   bitmap распределены по банкам 7, 0 и 1, построены вектор IM 2 и исполняемая цепочка
                ;   каждый проход выводит две картинки с атрибутами #90 и #A0, между вызовами SP восстановлен
                ;   Q и A меняют задержку, Space переводит управление в HaltFinal, обычного RET нет
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', I, IM, IFF, R, стек, таблица IM 2, экран, цепочка, операнды и 7FFD
                ; Note:
                ;   три bitmap из #62A9 копируются до перезаписи части исходного файла по #8000
                ;   места #912A и #9EE6 попеременно содержат NOP либо LD SP,#6196 и HALT
                ;   девять сценариев сверили обе картинки, три IRQ за пару выводов, клавиши и выход до HALT
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
                LD HL, #616C
                LD (#BFC0), HL
                IM 2
                CALL @Final.PrepareFrame.Entry
                ; ожидание IRQ перед подготовкой двух мест переключения страницы в создаваемой цепочке
BeginFramePair: EI
                HALT
                EI
                LD HL, (#62A7)
                LD (HL), #00
                INC HL
                LD (HL), #00
                INC HL
                LD (HL), #00
                INC HL
                LD (HL), #00
                LD HL, (#62A5)
                LD (HL), #31
                INC HL
                LD DE, #6196
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                LD (HL), #76
                LD BC, #7FFD
                LD A, #08
                OUT (C), A
                LD A, #00
                LD (#6173), A
                LD A, #90
                EX AF, AF'
                CALL #8000
                LD BC, #7FFD
                LD A, #01
                OUT (C), A
                LD (#6173), A
                LD HL, (#62A5)
                LD (HL), #00
                INC HL
                LD (HL), #00
                INC HL
                LD (HL), #00
                INC HL
                LD (HL), #00
                LD HL, (#62A7)
                LD (HL), #31
                INC HL
                LD DE, #6196
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
                CALL #8000
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
