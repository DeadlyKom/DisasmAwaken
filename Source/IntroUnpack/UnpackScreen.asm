                module IntroUnpack
                module UnpackScreen
; Документация [IntroUnpack](../../Docs/FunctionDetails/IntroUnpack.md)
; -----------------------------------------
; Распаковка экранного потока после переноса из #8931 в #6E31
; исходная запись 3, файловые смещения #2631..#26CA
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
Entry:          LD DE, #4000
                EXX
                LD DE, #008E
                INC E
                CALL #1FC6
                ADD HL, DE
Point6E3D:      LD A, (HL)
                INC HL
                LD IXL, #FF
Point6E42:      EXX
                JR NZ, @IntroUnpack.UnpackScreen.Point6EA0                      ; переход, если флаг Z сброшен


                LD B, #01
Point6E47:      EX AF, AF'
                SLA D
                JR NZ, @IntroUnpack.UnpackScreen.Point6E50                      ; переход, если флаг Z сброшен


                LD D, (HL)
                INC HL
                SLL D
Point6E50:      DJNZ @IntroUnpack.UnpackScreen.Point6E82

                JR C, @IntroUnpack.UnpackScreen.Point6E3D                       ; переход, если флаг Carry установлен


                INC B
Point6E55:      LD C, #56
                LD A, #FE
Point6E59:      SLA D
                JR NZ, @IntroUnpack.UnpackScreen.Point6E61                      ; переход, если флаг Z сброшен


                LD D, (HL)
                INC HL
                RL D
Point6E61:      RLA
                SLA C
                JR Z, @IntroUnpack.UnpackScreen.Point6E6D                       ; переход, если флаг Z установлен


                JR C, @IntroUnpack.UnpackScreen.Point6E59                       ; переход, если флаг Carry установлен


                RRCA
                JR NC, @IntroUnpack.UnpackScreen.Point6E59                      ; переход, если флаг Carry сброшен


                SUB #08
Point6E6D:      ADD A, #09
                DJNZ @IntroUnpack.UnpackScreen.Point6E47

                CP #F9
                JR NZ, @IntroUnpack.UnpackScreen.Point6E77                      ; переход, если флаг Z сброшен


                LD A, (HL)
                INC HL
Point6E77:      ADC A, #FF
                LD IXL, A
                JR C, @IntroUnpack.UnpackScreen.Point6E55                       ; переход, если флаг Carry установлен


                LD HL, #2758
                EXX
                RET


Point6E82:      LD A, (HL)
                INC HL
                EXX
                LD L, A
                EX AF, AF'
                LD H, A
                ADD HL, DE
                CP #FD
                JR NC, @IntroUnpack.UnpackScreen.Point6E8F                      ; переход, если флаг Carry сброшен


                DEC IXL
Point6E8F:      LD A, H
                CP #58
                JR NC, @IntroUnpack.UnpackScreen.Point6EBF                      ; переход, если флаг Carry сброшен


                XOR L
                AND #F8
                XOR L
                LD B, A
                XOR L
                XOR H
                RLCA
                RLCA
                LD C, A
Point6E9E:      EX AF, AF'
                LD A, (BC)
Point6EA0:      EX AF, AF'
                LD A, D
                CP #58
                JR NC, @IntroUnpack.UnpackScreen.Point6EC0                      ; переход, если флаг Carry сброшен


                XOR E
                AND #F8
                XOR E
                LD B, A
                XOR E
                XOR D
                RLCA
                RLCA
                LD C, A
Point6EB0:      EX AF, AF'
                LD (BC), A
                INC DE
                JR NC, @IntroUnpack.UnpackScreen.Point6EB7                      ; переход, если флаг Carry сброшен


                DEC HL
                DEC HL
Point6EB7:      INC HL
                EX AF, AF'
                INC IXL
                JR NZ, @IntroUnpack.UnpackScreen.Point6E8F                      ; переход, если флаг Z сброшен


                JR @IntroUnpack.UnpackScreen.Point6E42


Point6EBF:      SCF
Point6EC0:      PUSH AF
                ADD A, #00
                LD B, A
                POP AF
                LD C, E
                JR NC, @IntroUnpack.UnpackScreen.Point6EB0                      ; переход, если флаг Carry сброшен


                LD C, L
                JR @IntroUnpack.UnpackScreen.Point6E9E


                endmodule
                endmodule
