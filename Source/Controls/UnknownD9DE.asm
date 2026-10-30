                module Controls
                module UnknownD9DE
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #19DE..#1AB8
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
Entry:          LD A, #AF
                EX AF, AF'
                LD A, (#CEF9)
                CP #04
                LD A, (#D180)
                RET NC                                                          ; выход, если флаг Carry сброшен

                CP #09
                RET NC                                                          ; выход, если флаг Carry сброшен

                CP #02
                RET C                                                           ; выход, если флаг Carry установлен

                CALL @Controls.UnknownD9B0.Entry
                LD HL, (#D17D)
                LD A, (#D17F)
                LD B, A
                LD A, #7F
                CP H
                JR C, @Controls.UnknownD9DE.PointDA17                           ; переход, если флаг Carry установлен


                ADD A, H
                RRC B
                JR C, @Controls.UnknownD9DE.PointDA06                           ; переход, если флаг Carry установлен


                SUB H
                SUB H
PointDA06:      LD C, A
                CP #08
                JR NC, @Controls.UnknownD9DE.PointDA0C                          ; переход, если флаг Carry сброшен


                INC D
PointDA0C:      CP #F8
                JR C, @Controls.UnknownD9DE.PointDA12                           ; переход, если флаг Carry установлен


                INC D
                INC D
PointDA12:      LD A, #48
                CP L
                JR NC, @Controls.UnknownD9DE.PointDA19                          ; переход, если флаг Carry сброшен


PointDA17:      XOR A
                RET


PointDA19:      LD A, #30
                ADD A, L
                RRC B
                JR NC, @Controls.UnknownD9DE.PointDA22                          ; переход, если флаг Carry сброшен


                SUB L
                SUB L
PointDA22:      ADD A, E
                LD L, A
                LD A, C
                LD H, #04
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                SRL C
                SRL C
                SRL C
                LD B, #00
                ADD HL, BC
                AND #07
                LD C, A
                PUSH IX
                LD IX, #D990
                LD IY, (#D240)
                XOR A
PointDA43:      PUSH AF
                LD A, IYL
                XOR IYH
                LD IYL, A
                LD A, L
                SUB #20
                LD L, A
                JR NC, @Controls.UnknownD9DE.PointDA51                          ; переход, если флаг Carry сброшен


                DEC H
PointDA51:      LD A, H
                CP #60
                JR C, @Controls.UnknownD9DE.PointDA5E                           ; переход, если флаг Carry установлен


                CP #8C
                JR NC, @Controls.UnknownD9DE.PointDAA2                          ; переход, если флаг Carry сброшен


                CP #80
                JR C, @Controls.UnknownD9DE.PointDAA2                           ; переход, если флаг Carry установлен


PointDA5E:      PUSH HL
                LD A, (IX + #00)
                LD B, #08
PointDA64:      RLCA
                RR H
                DJNZ @Controls.UnknownD9DE.PointDA64

                ADD A, A
                LD L, A
                LD A, #08
                SUB C
                LD B, A
                XOR A
PointDA70:      ADD HL, HL
                RLA
                DJNZ @Controls.UnknownD9DE.PointDA70

                LD B, D
                EX DE, HL
                EX (SP), HL
                RRC B
                JR C, @Controls.UnknownD9DE.PointDA89                           ; переход, если флаг Carry установлен


                DEC HL
                LD (#DA83), A
                CPL
                AND (HL)
                LD (HL), A
                LD A, #00
                AND IYL
                OR (HL)
                LD (HL), A
                INC HL
PointDA89:      LD A, D
                CPL
                AND (HL)
                LD (HL), A
                LD A, D
                AND IYL
                OR (HL)
                LD (HL), A
                RRC B
                JR C, @Controls.UnknownD9DE.PointDAA1                           ; переход, если флаг Carry установлен


                INC HL
                LD A, E
                CPL
                AND (HL)
                LD (HL), A
                LD A, E
                AND IYL
                OR (HL)
                LD (HL), A
                DEC HL
PointDAA1:      POP DE
PointDAA2:      POP AF
                BIT 7, D
                JR NZ, @Controls.UnknownD9DE.PointDAB1                          ; переход, если флаг Z сброшен


                INC A
                INC IX
                CP E
                JR NZ, @Controls.UnknownD9DE.PointDA43                          ; переход, если флаг Z сброшен


                SET 7, D
                DEC IX
PointDAB1:      DEC IX
                DEC A
                JR NZ, @Controls.UnknownD9DE.PointDA43                          ; переход, если флаг Z сброшен


                POP IX
                RET


                endmodule
                endmodule
