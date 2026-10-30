                module Controls
                module UnknownD236
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1236..#130A
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
Entry:          LD BC, (#D17D)
                LD (#D181), BC
                LD IX, #0000
                LD DE, (#D17F)
                LD A, #30
                BIT 1, E
                JR NZ, @Controls.UnknownD236.PointD24E                          ; переход, если флаг Z сброшен


                ADD A, C
                ADD A, C
PointD24E:      SUB C
                LD (#D183), A
                LD A, #80
                BIT 0, E
                JR Z, @Controls.UnknownD236.PointD25A                           ; переход, если флаг Z установлен


                ADD A, B
                ADD A, B
PointD25A:      SUB B
                LD (#D184), A
                LD A, C
                CP #30
                BIT 3, E
                EX AF, AF'
                LD A, B
                CP #78
                BIT 2, E
                JR Z, @Controls.UnknownD236.PointD277                           ; переход, если флаг Z установлен


                JR NC, @Controls.UnknownD236.PointD278                          ; переход, если флаг Carry сброшен


                EX AF, AF'
                JR Z, @Controls.UnknownD236.PointD274                           ; переход, если флаг Z установлен


                JR NC, @Controls.UnknownD236.PointD2AA                          ; переход, если флаг Carry сброшен


                JR @Controls.UnknownD236.PointD282


PointD274:      RET NC                                                          ; выход, если флаг Carry сброшен

                JR @Controls.UnknownD236.PointD2AA


PointD277:      RET NC                                                          ; выход, если флаг Carry сброшен

PointD278:      EX AF, AF'
                JR Z, @Controls.UnknownD236.PointD27F                           ; переход, если флаг Z установлен


                JR NC, @Controls.UnknownD236.PointD2DA                          ; переход, если флаг Carry сброшен


                JR @Controls.UnknownD236.PointD297


PointD27F:      RET NC                                                          ; выход, если флаг Carry сброшен

                JR @Controls.UnknownD236.PointD2DA


PointD282:      LD A, B
                ADD A, D
                JR C, @Controls.UnknownD236.PointD28B                           ; переход, если флаг Carry установлен


                CP #78
                JP C, @Controls.UnknownD30B.PointD314                           ; переход, если флаг Carry установлен


PointD28B:      LD A, D
                SUB B
                JR C, @Controls.UnknownD236.PointD291                           ; переход, если флаг Carry установлен


                CP #78
PointD291:      JP C, @Controls.UnknownD320.PointD3E4                           ; переход, если флаг Carry установлен


                JP @Controls.UnknownD320.PointD34A


PointD297:      LD A, B
                SUB #78
                LD B, A
                LD (#D182), A
                LD A, D
                SUB B
                RET C                                                           ; выход, если флаг Carry установлен

                RET Z                                                           ; выход, если флаг Z установлен

                SUB #F0
                JP NC, @Controls.UnknownD320.PointD340                          ; переход, если флаг Carry сброшен


                JP @Controls.UnknownD320.PointD3DA


PointD2AA:      LD A, C
                SUB #30
                LD C, A
                LD (#D181), A
                LD A, D
                SUB C
                RET C                                                           ; выход, если флаг Carry установлен

                LD A, D
                CALL @Controls.UnknownD30B.Entry
                LD H, D
                LD L, E
                LD A, C
                CALL @Controls.UnknownD30B.Entry
                SBC HL, DE
                LD A, #78
                SUB B
                CALL @Controls.UnknownD30B.Entry
                SBC HL, DE
                JP C, @Controls.UnknownD320.PointD485                           ; переход, если флаг Carry установлен


                ADD HL, DE
                LD A, #78
                ADD A, B
                CALL @Controls.UnknownD30B.Entry
                SBC HL, DE
                JP NC, @Controls.UnknownD320.PointD396                          ; переход, если флаг Carry сброшен


                JP @Controls.UnknownD320.PointD40E


PointD2DA:      LD A, B
                SUB #78
                LD B, A
                LD A, C
                SUB #30
                LD C, A
                LD (#D181), BC
                LD A, D
                CALL @Controls.UnknownD30B.Entry
                LD H, D
                LD L, E
                LD A, C
                CALL @Controls.UnknownD30B.Entry
                SBC HL, DE
                RET C                                                           ; выход, если флаг Carry установлен

                LD A, B
                CALL @Controls.UnknownD30B.Entry
                SBC HL, DE
                RET C                                                           ; выход, если флаг Carry установлен

                ADD HL, DE
                LD A, B
                ADD A, #F8
                JR C, @Controls.UnknownD236.PointD308                           ; переход, если флаг Carry установлен


                CALL @Controls.UnknownD30B.Entry
                SBC HL, DE
                JP NC, @Controls.UnknownD320.PointD38C                          ; переход, если флаг Carry сброшен


PointD308:      JP @Controls.UnknownD320.PointD404


                endmodule
                endmodule
