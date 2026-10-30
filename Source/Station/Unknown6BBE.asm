                module Station
                module Unknown6BBE
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #0E6A..#0EAB
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
Entry:          EX DE, HL
                LD HL, #0800
                LD (#6320), HL
                LD HL, #DECB
                PUSH DE
                LD A, E
                CALL @Station.PrintAfterCR.Entry
                LD A, #08
                LD (#6321), A
                POP HL
                LD BC, #9728
                ADD HL, BC
Point6BD7:      XOR A
                EX AF, AF'
Point6BD9:      LD A, (@TextStreamState.Column2X)
                LD (#6320), A
                LD A, (HL)
                OR A
                RET Z                                                           ; выход, если флаг Z установлен

                CALL @Station.UnknownBDF0.Entry
                INC HL
                EX AF, AF'
                INC A
                EX AF, AF'
                JR C, @Station.Unknown6BBE.Point6BEF                            ; переход, если флаг Carry установлен


                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

Point6BEF:      LD A, (#AEAB)
                LD C, A
                LD A, (#6321)
                ADD A, #08
                CP C
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD (#6321), A
                JP @Station.Unknown6BBE.Point6BD9


                endmodule
                endmodule
