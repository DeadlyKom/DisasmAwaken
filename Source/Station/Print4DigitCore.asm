                module Station
                module Print4DigitCore
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [числовой вывод](../../Docs/NumberOutput.md)
; -----------------------------------------
; Вывод частного тысяч и трёх десятичных разрядов с подавлением ведущих нулей
; исходная запись 4, файловые смещения #5CAB..#5D00
; In:
;   BC - беззнаковое слово, десятичные цифры соответствуют числу только в диапазоне 0..9999
;   TextWindow и исходный код DrawGlyph подготовлены для вывода
; Out:
;   BC - значение перед последним вызовом DrawGlyph, при полном успехе равно 10
;   AF - результат последнего DrawGlyph, при успехе #0045, при отказе Carry сброшен и A содержит код причины
;   при BC<1000 ведущие нулевые разряды пропущены, единицы выводятся всегда
;   при BC>=1000 коды равны #30+BC/1000, #30+(BC/100)%10, #30+(BC/10)%10, #30+BC%10, деление целое
; Corrupt:
;   BC, AF
; Note:
;   HL, DE, альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   вывод выполняется через DrawGlyph с его ограничениями окна и самомодификацией, текстовый курсор продвигается
;   при первом отказе DrawGlyph дальнейшие символы не вызываются, уже выведенные символы не отменяются
;   при допустимом пропуске глифа за отрицательным краем DrawGlyph возвращает успех, это не отказ числового вывода
;   E хранит признак уже начатого числа, исходный DE восстановлен перед возвратом
;   частное тысяч не ограничено девятью, например 65535 даёт коды #71, #35, #33, #35
; -----------------------------------------
Entry:          PUSH HL
                PUSH DE
                LD H, B
                LD L, C
                ; расчёт очередной цифры повторным вычитанием делителя 1000 из остатка
                LD BC, @NumberConst.Thousand
                XOR A
                DEC A
ThousandsLoop:  INC A
                SBC HL, BC
                JR NC, @Station.Print4DigitCore.ThousandsLoop                   ; переход, если остаток не меньше делителя, накопление частного продолжается

                ; восстановление остатка после последнего вычитания с заёмом
                ADD HL, BC
                AND A
                LD E, A
                JR Z, @Station.Print4DigitCore.Hundreds                         ; переход, если частное тысяч равно нулю, ведущий разряд не выводится

                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JR NC, @Station.Print4DigitCore.Restore                         ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                ; расчёт очередной цифры повторным вычитанием делителя 100 из остатка
Hundreds:       LD BC, @NumberConst.Hundred
                XOR A
                DEC A
HundredsLoop:   INC A
                SBC HL, BC
                JR NC, @Station.Print4DigitCore.HundredsLoop                    ; переход, если остаток не меньше делителя, накопление частного продолжается

                ; восстановление остатка после последнего вычитания с заёмом
                ADD HL, BC
                INC E
                DEC E
                JR NZ, @Station.Print4DigitCore.PrintHundreds                   ; переход, если предыдущий разряд уже выведен, сотни обязательны даже при нуле

                AND A
                LD E, A
                JR Z, @Station.Print4DigitCore.Tens                             ; переход, если сотни равны нулю и число ещё не начато, ведущий ноль пропускается

PrintHundreds:  ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JR NC, @Station.Print4DigitCore.Restore                         ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                ; расчёт очередной цифры повторным вычитанием делителя 10 из остатка
Tens:           LD BC, @NumberConst.Ten
                XOR A
                DEC A
TensLoop:       INC A
                SBC HL, BC
                JR NC, @Station.Print4DigitCore.TensLoop                        ; переход, если остаток не меньше делителя, накопление частного продолжается

                ; восстановление остатка после последнего вычитания с заёмом
                ADD HL, BC
                INC E
                DEC E
                JR NZ, @Station.Print4DigitCore.PrintTens                       ; переход, если предыдущий разряд уже выведен, десятки обязательны даже при нуле

                AND A
                JR Z, @Station.Print4DigitCore.Units                            ; переход, если десятки равны нулю и число ещё не начато, вывод начинается с единиц

PrintTens:      ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JR NC, @Station.Print4DigitCore.Restore                         ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                ; преобразование оставшихся единиц в код цифры, этот разряд выводится и для нулевого числа
Units:          LD A, L
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
Restore:        POP DE
                POP HL
                RET

                endmodule
                endmodule
