                module Controls
                module UnknownCF0B
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0F0B..#10C9
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
Entry:          EXX
                LD BC, #0003
                EXX
                LD A, (#CEF9)
                AND A
                JP NZ, @Controls.UnknownCF0B.PointCFBF                          ; переход, если флаг Z сброшен


                LD A, (#9B26)
                BIT 7, A
                JP NZ, @Controls.UnknownD10A.PointD154                          ; переход, если флаг Z сброшен


                AND #7F
                LD (#9B26), A
                LD HL, (#9B25)
                EX DE, HL
                LD HL, (#9B1F)
                LD A, (#9B24)
                LD B, A
                LD A, (#9B1E)
                LD C, A
                LD A, H
                BIT 7, A
                JR NZ, @Controls.UnknownCF0B.PointCF3C                          ; переход, если флаг Z сброшен


                EXX
                SET 0, B
                EXX
PointCF3C:      AND #7F
                LD H, A
                CALL @Controls.UnknownD0CA.Entry
                LD A, D
                LD (#D17E), A
                LD HL, (#9B25)
                EX DE, HL
                LD HL, (#9B22)
                LD A, (#9B24)
                LD B, A
                LD A, (#9B21)
                LD C, A
                LD A, H
                BIT 7, A
                JR NZ, @Controls.UnknownCF0B.PointCF5E                          ; переход, если флаг Z сброшен


                EXX
                SET 1, B
                EXX
PointCF5E:      AND #7F
                LD H, A
                CALL @Controls.UnknownD0CA.Entry
                LD A, D
                LD (#D17D), A
                EXX
                LD A, B
                EXX
                LD (#D17F), A
                LD A, (#9B26)
                AND A
                JR NZ, @Controls.UnknownCF0B.PointCF83                          ; переход, если флаг Z сброшен


                LD HL, #A000
                LD DE, (#9B24)
                SBC HL, DE
                JR C, @Controls.UnknownCF0B.PointCF83                           ; переход, если флаг Carry установлен


                LD A, #FF
                JR @Controls.UnknownCF0B.PointCFBC


PointCF83:      LD HL, #A000
                LD DE, (#9B25)
                OR A
                SBC HL, DE
                JP C, @Controls.UnknownD10A.PointD154                           ; переход, если флаг Carry установлен


                LD A, (#9B26)
                AND A
                JR Z, @Controls.UnknownCF0B.PointCFB2                           ; переход, если флаг Z установлен


                LD B, A
                LD A, (#9B25)
                LD C, A
                XOR A
                LD E, #A0
PointCF9E:      SLA C
                RL B
                JR C, @Controls.UnknownCF0B.PointCFA9                           ; переход, если флаг Carry установлен


                SLA E
                RLA
                JR @Controls.UnknownCF0B.PointCF9E


PointCFA9:      SCF
                RR B
                CALL @Controls.UnknownD167.Entry
                LD A, D
                JR @Controls.UnknownCF0B.PointCFBC


PointCFB2:      LD A, (#9B25)
                LD B, A
                LD A, #A0
                CALL @Controls.UnknownD165.Entry
                LD A, D
PointCFBC:      JP @Controls.UnknownCF0B.PointD0BD


PointCFBF:      DEC A
                JR NZ, @Controls.UnknownCF0B.PointCFED                          ; переход, если флаг Z сброшен


                LD A, (#9B26)
                BIT 7, A
                JP Z, @Controls.UnknownD10A.PointD154                           ; переход, если флаг Z установлен


                AND #7F
                LD (#9B26), A
                LD HL, (#9B25)
                EX DE, HL
                LD HL, (#9B1F)
                LD A, (#9B24)
                LD B, A
                LD A, (#9B1E)
                LD C, A
                LD A, H
                BIT 7, A
                JR Z, @Controls.UnknownCF0B.PointCFEA                           ; переход, если флаг Z установлен


                AND #7F
                LD H, A
                EXX
                SET 0, B
                EXX
PointCFEA:      JP @Controls.UnknownCF0B.PointCF3C


PointCFED:      DEC A
                JP NZ, @Controls.UnknownCF0B.PointD09A                          ; переход, если флаг Z сброшен


                LD A, (#9B20)
                BIT 7, A
                JP Z, @Controls.UnknownD10A.PointD154                           ; переход, если флаг Z установлен


                AND #7F
                LD (#9B20), A
                LD HL, (#9B1F)
                EX DE, HL
                LD HL, (#9B25)
                LD A, (#9B1E)
                LD B, A
                LD A, (#9B24)
                LD C, A
                LD A, H
                BIT 7, A
                JR NZ, @Controls.UnknownCF0B.PointD016                          ; переход, если флаг Z сброшен


                EXX
                SET 0, B
                EXX
PointD016:      AND #7F
                LD H, A
                CALL @Controls.UnknownD0CA.Entry
                LD A, D
                LD (#D17E), A
                LD HL, (#9B1F)
                EX DE, HL
                LD HL, (#9B22)
                LD A, (#9B1E)
                LD B, A
                LD A, (#9B21)
                LD C, A
                LD A, H
                BIT 7, A
                JR NZ, @Controls.UnknownCF0B.PointD038                          ; переход, если флаг Z сброшен


                EXX
                SET 1, B
                EXX
PointD038:      AND #7F
                LD H, A
                CALL @Controls.UnknownD0CA.Entry
                LD A, D
                LD (#D17D), A
                EXX
                LD A, B
                EXX
                LD (#D17F), A
                LD A, (#9B20)
                AND A
                JR NZ, @Controls.UnknownCF0B.PointD05D                          ; переход, если флаг Z сброшен


                LD HL, #A000
                LD DE, (#9B1E)
                SBC HL, DE
                JR C, @Controls.UnknownCF0B.PointD05D                           ; переход, если флаг Carry установлен


                LD A, #FF
                JR @Controls.UnknownCF0B.PointD097


PointD05D:      LD HL, #A000
                LD DE, (#9B1F)
                OR A
                SBC HL, DE
                JP C, @Controls.UnknownD10A.PointD154                           ; переход, если флаг Carry установлен


                LD A, (#9B20)
                AND A
                JR Z, @Controls.UnknownCF0B.PointD08D                           ; переход, если флаг Z установлен


                LD B, A
                LD A, (#9B1F)
                LD C, A
                XOR A
                LD E, #A0
PointD078:      SLA C
                RL B
                JR C, @Controls.UnknownCF0B.PointD084                           ; переход, если флаг Carry установлен


                SLA E
                RLA
                JP @Controls.UnknownCF0B.PointD078


PointD084:      SCF
                RR B
                CALL @Controls.UnknownD167.Entry
                LD A, D
                JR @Controls.UnknownCF0B.PointD097


PointD08D:      LD A, (#9B1F)
                LD B, A
                LD A, #A0
                CALL @Controls.UnknownD165.Entry
                LD A, D
PointD097:      JP @Controls.UnknownCF0B.PointD0BD


PointD09A:      LD A, (#9B20)
                BIT 7, A
                JP NZ, @Controls.UnknownD10A.PointD154                          ; переход, если флаг Z сброшен


                LD HL, (#9B1F)
                EX DE, HL
                LD HL, (#9B25)
                LD A, (#9B1E)
                LD B, A
                LD A, (#9B24)
                LD C, A
                LD A, H
                BIT 7, A
                JR Z, @Controls.UnknownCF0B.PointD0BA                           ; переход, если флаг Z установлен


                EXX
                SET 0, B
                EXX
PointD0BA:      JP @Controls.UnknownCF0B.PointD016


PointD0BD:      LD (#D180), A
                LD A, #01
                RET


PointD0C3:      LD H, L
                LD L, C
                LD D, E
                LD E, B
                JP @Controls.UnknownD0CA.PointD0EE


                endmodule
                endmodule
