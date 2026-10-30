                module Final
                module InitializeFinal
; Документация [Final](../../Docs/FunctionDetails/Final.md)
; -----------------------------------------
; Подготовка трёх экранных банков, таблицы IM 2 и финальной анимации
; исходная запись 29, файловые смещения #0000..#0122
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   три bitmap по #1800 байт из #62A9 последовательно копируются в банки 7, 0 и 1
;   адрес #8000 в исходном файле содержит bitmap, исполняемая цепочка создаётся там позже PrepareFrame
;   основной цикл перед исполнением заменяет один пропуск на четыре NOP, другой на LD SP,#6196 и HALT
;   два показа используют альтернативный A=#90 и #A0 как байты атрибутов
;   процедура циклическая, выход по Space ведёт к HaltFinal, а не в BASIC
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
Point607A:      EI
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
Point60D5:      NOP
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
                JP NZ, @Final.InitializeFinal.Point60D5                         ; переход, если флаг Z сброшен


                LD A, #A0
                EX AF, AF'
                CALL #8000
                LD A, #00
                OUT (#FE), A
                CALL @Final.ReadSpeedKeys.Entry
                LD A, #7F
                IN A, (#FE)
                RRA
                JP NC, @Final.HaltFinal.Entry                                   ; переход, если флаг Carry сброшен


                JP @Final.InitializeFinal.Point607A


                endmodule
                endmodule
