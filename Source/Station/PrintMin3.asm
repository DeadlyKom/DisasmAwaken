                module Station
                module PrintMin3
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [числовой вывод](../../Docs/NumberOutput.md)
; -----------------------------------------
; Вывод старым числовым ядром с дополнением слева минимум до трёх символов
; исходная запись 4, файловые смещения #5BD7..#5C00
; In:
;   BC - исходное беззнаковое слово, обычный десятичный результат для 0..9999
;   TextWindow и исходный код DrawGlyph подготовлены для вывода
; Out:
;   BC - значение перед последним вызовом DrawGlyph, при полном успехе равно 10
;   AF - результат последнего DrawGlyph, при успехе #0045, при отказе Carry сброшен и A содержит код причины
;   при полном успехе строка старого ядра дополнена слева кодом #30 минимум до 3 символов
; Corrupt:
;   BC, AF
; Note:
;   HL, DE, альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   вывод выполняется через DrawGlyph с его ограничениями окна и самомодификацией, текстовый курсор продвигается
;   при первом отказе DrawGlyph дальнейшие символы не вызываются, уже выведенные символы не отменяются
;   при допустимом пропуске глифа за отрицательным краем DrawGlyph возвращает успех, это не отказ числового вывода
;   при BC>=10000 сохраняется особенность Print4DigitCore, разряд десятков тысяч отдельно не выводится
; -----------------------------------------
Entry:          PUSH HL
                PUSH DE
                ; проверка числа относительно 99 для выбора ведущего разряда
Hundreds:       LD HL, @NumberConst.Max2Digits
                OR A
                SBC HL, BC
                JP C, @Station.PrintMin3.Number                                 ; переход, если число больше 99, два ведущих нуля не нужны

                LD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JP NC, @Station.PrintMin3.Restore                               ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                ; проверка числа относительно 9 для выбора ведущего разряда
Tens:           LD HL, @NumberConst.Max1Digit
                OR A
                SBC HL, BC
                JP C, @Station.PrintMin3.Number                                 ; переход, если число больше 9, второй ведущий ноль не нужен

                LD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JP NC, @Station.PrintMin3.Restore                               ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

Number:         CALL @Station.Print4DigitCore.Entry
Restore:        POP DE
                POP HL
                RET

                endmodule
                endmodule
