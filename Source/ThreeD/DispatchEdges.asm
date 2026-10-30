                module ThreeD
                module DispatchEdges
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; Перебор индексов вершин и вызов обработчиков из таблиц #CF00 и #D000
; исходная запись 19, файловые смещения #0000..#0070
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
Entry:          XOR A
                LD (#CF03), A
                LD (#9BA3), A
                LD (#CF07), A
                PUSH HL
                LD A, B
                DEC A
                ADD A, L
                LD L, A
                LD A, H
                ADC A, #00
                LD H, A
                LD L, (HL)
                LD H, #8E
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                LD (#CF1B), DE
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                LD (#CF1D), DE
                LD A, (HL)
                LD (#CF1F), A
PointC02A:      LD HL, (#CF1B)
                LD (#CF0B), HL
                LD HL, (#CF1D)
                LD (#CF0D), HL
                LD A, (#CF1F)
                LD (#CF0F), A
                POP HL
                LD A, (HL)
                INC HL
                PUSH HL
                PUSH BC
                LD L, A
                LD H, #8E
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                LD (#CF1B), DE
                LD E, (HL)
                INC L
                LD D, (HL)
                INC L
                LD (#CF1D), DE
                LD A, (HL)
                LD (#CF1F), A
                LD A, (#CF0F)
                CPL
                AND #F0
                LD L, A
                LD A, (#CF1F)
                AND #0F
                OR L
                LD L, A
                LD H, #CF
                LD E, (HL)
                INC H
                LD D, (HL)
                EX DE, HL
                LD DE, #C071
                PUSH DE
                JP (HL)


                endmodule
                endmodule
