                module Action
                module MultiplySignedScaled
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Знаковое умножение с масштабом 1/128 для коэффициента от -127 до 127, выход через JP (IX)
; исходная запись 17, файловые смещения #712C..#7193
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
Entry:          LD L, A
                XOR D
                EX AF, AF'
                BIT 7, D
                JR Z, @Action.MultiplySignedScaled.PointD13A                    ; переход, если флаг Z установлен


                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
PointD13A:      LD A, L
                AND A
                JP P, @Action.MultiplySignedScaled.PointD141                    ; переход, если флаг Sign сброшен


                NEG
PointD141:      LD C, #00
                LD H, C
                LD L, C
                ADD A, A
                ADD A, A
                JR C, @Action.MultiplySignedScaled.PointD15E                    ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.MultiplySignedScaled.PointD164                    ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.MultiplySignedScaled.PointD16A                    ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.MultiplySignedScaled.PointD170                    ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.MultiplySignedScaled.PointD176                    ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.MultiplySignedScaled.PointD17C                    ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.MultiplySignedScaled.PointD182                    ; переход, если флаг Carry установлен


                JP @Action.MultiplySignedScaled.PointD188


PointD15E:      ADD HL, DE
                ADC A, C
                ADD HL, HL
                ADC A, A
                JR NC, @Action.MultiplySignedScaled.PointD166                   ; переход, если флаг Carry сброшен


PointD164:      ADD HL, DE
                ADC A, C
PointD166:      ADD HL, HL
                ADC A, A
                JR NC, @Action.MultiplySignedScaled.PointD16C                   ; переход, если флаг Carry сброшен


PointD16A:      ADD HL, DE
                ADC A, C
PointD16C:      ADD HL, HL
                ADC A, A
                JR NC, @Action.MultiplySignedScaled.PointD172                   ; переход, если флаг Carry сброшен


PointD170:      ADD HL, DE
                ADC A, C
PointD172:      ADD HL, HL
                ADC A, A
                JR NC, @Action.MultiplySignedScaled.PointD178                   ; переход, если флаг Carry сброшен


PointD176:      ADD HL, DE
                ADC A, C
PointD178:      ADD HL, HL
                ADC A, A
                JR NC, @Action.MultiplySignedScaled.PointD17E                   ; переход, если флаг Carry сброшен


PointD17C:      ADD HL, DE
                ADC A, C
PointD17E:      ADD HL, HL
                ADC A, A
                JR NC, @Action.MultiplySignedScaled.PointD184                   ; переход, если флаг Carry сброшен


PointD182:      ADD HL, DE
                ADC A, C
PointD184:      ADD HL, HL
                ADC A, A
                LD L, H
                LD H, A
PointD188:      EX AF, AF'
                JP P, @Action.MultiplySignedScaled.PointD192                    ; переход, если флаг Sign сброшен


                EX DE, HL
                LD HL, #0000
                SBC HL, DE
PointD192:      JP (IX)


                endmodule
                endmodule
