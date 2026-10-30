                module Controls
                module UnknownD57B
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #157B..#1608
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
Entry:          LD A, (#D18C)
                AND A
                LD A, L
                AND #E0
                OR #01
                LD E, A
                LD C, #FF
                LD B, #00
                RET


PointD58A:      LD HL, #FFE0
                LD (#D5B5), HL
                LD HL, #3880
                JR @Controls.UnknownD57B.PointD59E


PointD595:      LD HL, #0020
                LD (#D5B5), HL
                LD HL, #308C
PointD59E:      LD (#D600), HL
                PUSH DE
                PUSH AF
                LD L, A
                LD H, #04
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD DE, #001F
                ADD HL, DE
                PUSH BC
                DEC B
                INC B
                JR Z, @Controls.UnknownD57B.PointD605                           ; переход, если флаг Z установлен


                LD DE, #0020
PointD5B7:      LD C, L
                LD A, IXL
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                LD L, C
                ADD HL, DE
                LD A, IXL
                XOR IXH
                LD IXL, A
                LD A, H
                CP #00
                JR NC, @Controls.UnknownD57B.PointD605                          ; переход, если флаг Carry сброшен


                DJNZ @Controls.UnknownD57B.PointD5B7

PointD605:      POP BC
                POP AF
                POP DE
                RET


                endmodule
                endmodule
