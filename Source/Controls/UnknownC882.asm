                module Controls
                module UnknownC882
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0882..#0A8C
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          LD (#CA8A), SP
PointC886:      LD (#CA84), A
                LD SP, HL
                LD L, #10
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #20
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #30
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #40
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #50
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #60
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #70
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #80
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #90
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #A0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #B0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #C0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #D0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #E0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #F0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                LD SP, HL
                LD L, #00
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                LD DE, #F910
                ADD HL, DE
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                INC H
                LD A, #00
                DEC A
                JP NZ, @Controls.UnknownC882.PointC886                          ; переход, если флаг Z сброшен


                LD SP, #0000
                RET


                endmodule
                endmodule
