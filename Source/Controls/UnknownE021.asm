                module Controls
                module UnknownE021
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #0543..#066F
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
Entry:          LD (#E089), SP
                LD HL, #0000
                LD SP, #48B8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #49B8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4AB8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4BB8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4CB8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4DB8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4EB8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4FB8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #48D8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #49D8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4AD8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4BD8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4CD8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4DD8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4ED8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #4FD8
                PUSH HL
                DEC SP
                PUSH HL
                LD SP, #0000
                LD A, (#9B81)
                DEC A
                JR Z, @Controls.UnknownE021.PointE0CA                           ; переход, если флаг Z установлен


                LD A, (#9B8A)
                ADD A, #A0
                JP PO, @Controls.UnknownE021.PointE09B                          ; переход, если флаг P/V сброшен


                LD A, #98
PointE09B:      CP #98
                JR NC, @Controls.UnknownE021.PointE0A1                          ; переход, если флаг Carry сброшен


                LD A, #98
PointE0A1:      CP #A6
                JR C, @Controls.UnknownE021.PointE0A7                           ; переход, если флаг Carry установлен


                LD A, #A5
PointE0A7:      LD C, A
                LD A, (#9B8B)
                ADD A, #70
                CP #68
                JR NC, @Controls.UnknownE021.PointE0B3                          ; переход, если флаг Carry сброшен


                LD A, #68
PointE0B3:      CP #76
                JR C, @Controls.UnknownE021.PointE0B9                           ; переход, если флаг Carry установлен


                LD A, #75
PointE0B9:      LD B, A
                LD A, (#9B8C)
                AND A
                LD DE, #E1B1
                JP P, @Controls.UnknownE021.PointE0C7                           ; переход, если флаг Sign сброшен


                LD DE, #E1E1
PointE0C7:      CALL @Controls.UnknownE14E.Entry
PointE0CA:      LD A, (#9B87)
                LD C, A
                LD A, (#9B88)
                OR C
                LD C, A
                LD A, (#9B89)
                OR C
                CP #80
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, (#9B87)
                ADD A, #A0
                JP PO, @Controls.UnknownE021.PointE0E4                          ; переход, если флаг P/V сброшен


                LD A, #98
PointE0E4:      CP #98
                JR NC, @Controls.UnknownE021.PointE0EA                          ; переход, если флаг Carry сброшен


                LD A, #98
PointE0EA:      CP #A6
                JR C, @Controls.UnknownE021.PointE0F0                           ; переход, если флаг Carry установлен


                LD A, #A5
PointE0F0:      LD C, A
                LD A, (#9B88)
                ADD A, #70
                CP #68
                JR NC, @Controls.UnknownE021.PointE0FC                          ; переход, если флаг Carry сброшен


                LD A, #68
PointE0FC:      CP #76
                JR C, @Controls.UnknownE021.PointE102                           ; переход, если флаг Carry установлен


                LD A, #75
PointE102:      LD B, A
                LD A, (#9B89)
                AND A
                LD DE, #E211
                JP P, @Controls.UnknownE021.PointE110                           ; переход, если флаг Sign сброшен


                LD DE, #E241
PointE110:      CALL @Controls.UnknownE14E.Entry
                LD A, (#9B82)
                AND A
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, (#9B85)
                ADD A, #B8
                JP PO, @Controls.UnknownE021.PointE122                          ; переход, если флаг P/V сброшен


                LD A, #B0
PointE122:      CP #B0
                JR NC, @Controls.UnknownE021.PointE128                          ; переход, если флаг Carry сброшен


                LD A, #B0
PointE128:      CP #BE
                JR C, @Controls.UnknownE021.PointE12E                           ; переход, если флаг Carry установлен


                LD A, #BD
PointE12E:      LD C, A
                LD A, (#9B84)
                ADD A, #70
                CP #68
                JR NC, @Controls.UnknownE021.PointE13A                          ; переход, если флаг Carry сброшен


                LD A, #68
PointE13A:      CP #76
                JR C, @Controls.UnknownE021.PointE140                           ; переход, если флаг Carry установлен


                LD A, #75
PointE140:      LD B, A
                LD A, (#9B86)
                AND A
                LD DE, #E211
                JP P, @Controls.UnknownE14E.Entry                               ; переход, если флаг Sign сброшен


                LD DE, #E241
                ; JP @Controls.UnknownE14E.Entry, продолжение в UnknownE14E.asm

                endmodule
                endmodule
