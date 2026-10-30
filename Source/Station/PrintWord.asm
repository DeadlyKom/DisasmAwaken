                module Station
                module PrintWord
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [числовой вывод](../../Docs/NumberOutput.md)
; -----------------------------------------
; Десятичный вывод беззнакового слова с байтовым бюджетом ведущих нулей
; исходная запись 4, файловые смещения #5C01..#5CAA
; In:
;   BC - беззнаковое число 0..65535
;   AF - A байтовый бюджет ведущих нулей, значения 0..4 дают обычное дополнение
;   TextWindow и исходный код DrawGlyph подготовлены для вывода
; Out:
;   BC - значение перед последним вызовом DrawGlyph, при полном успехе равно 10
;   AF - результат последнего DrawGlyph, при успехе #0045, при отказе Carry сброшен и A содержит код причины
;   числа 10000..65535 выводятся пятью цифрами независимо от входного A
;   при числе меньше 10000 и A в 0..4 перед цифрами добавляется min(A, 5-число цифр) нулей
; Corrupt:
;   BC, AF
; Note:
;   HL, DE, альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   вывод выполняется через DrawGlyph с его ограничениями окна и самомодификацией, текстовый курсор продвигается
;   при первом отказе DrawGlyph дальнейшие символы не вызываются, уже выведенные символы не отменяются
;   при допустимом пропуске глифа за отрицательным краем DrawGlyph возвращает успех, это не отказ числового вывода
;   AF' используется для хранения бюджета между глифами, но исходный AF' восстановлен
;   для каждого выполненного сравнения N<=9999, 999, 99, 9 бюджет уменьшается по модулю 256
;   после такого DEC ноль выводится только при сброшенном Sign, поэтому A=128..131 имеет особое поведение
;   пятизначная ветвь отделяет старшую цифру, затем принудительно дополняет остаток до четырёх цифр
;   это бюджет дополнительных нулей, например число 7 при A=2 выводится как 007, а не ширина поля два
; -----------------------------------------
Entry:          PUSH HL
                PUSH DE
                ; сохранение исходного AF' перед использованием альтернативного A для бюджета нулей
                EX AF, AF'
                PUSH AF
                EX AF, AF'
                ; проверка числа относительно 9999 для выбора ведущего разряда
                LD HL, @NumberConst.Max4Digits
                OR A
                SBC HL, BC
                JP C, @Station.PrintWord.FiveDigits                             ; переход, если число больше 9999, требуется отдельная цифра десятков тысяч

                ; расчёт следующего байтового бюджета ведущих нулей, переполнение сохраняется
                DEC A
                JP M, @Station.PrintWord.Thousands                              ; переход, если результат уменьшения бюджета имеет бит 7, ноль этого разряда пропускается

                EX AF, AF'
                LD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JP NC, @Station.PrintWord.Restore                               ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                EX AF, AF'
                ; проверка числа относительно 999 для выбора ведущего разряда
Thousands:      LD HL, @NumberConst.Max3Digits
                OR A
                SBC HL, BC
                JP C, @Station.PrintWord.Hundreds                               ; переход, если число больше 999, дополнение этого разряда не требуется

                ; расчёт следующего байтового бюджета ведущих нулей, переполнение сохраняется
                DEC A
                JP M, @Station.PrintWord.Hundreds                               ; переход, если результат уменьшения бюджета имеет бит 7, ноль этого разряда пропускается

                EX AF, AF'
                LD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JP NC, @Station.PrintWord.Restore                               ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                EX AF, AF'
                ; проверка числа относительно 99 для выбора ведущего разряда
Hundreds:       LD HL, @NumberConst.Max2Digits
                OR A
                SBC HL, BC
                JP C, @Station.PrintWord.Tens                                   ; переход, если число больше 99, дополнение этого разряда не требуется

                ; расчёт следующего байтового бюджета ведущих нулей, переполнение сохраняется
                DEC A
                JP M, @Station.PrintWord.Tens                                   ; переход, если результат уменьшения бюджета имеет бит 7, ноль этого разряда пропускается

                EX AF, AF'
                LD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JP NC, @Station.PrintWord.Restore                               ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                EX AF, AF'
                ; проверка числа относительно 9 для выбора ведущего разряда
Tens:           LD HL, @NumberConst.Max1Digit
                OR A
                SBC HL, BC
                JP C, @Station.PrintWord.Number                                 ; переход, если число больше 9, дополнение разряда десятков не требуется

                ; расчёт следующего байтового бюджета ведущих нулей, переполнение сохраняется
                DEC A
                JP M, @Station.PrintWord.Number                                 ; переход, если результат уменьшения бюджета имеет бит 7, ноль этого разряда пропускается

                EX AF, AF'
                LD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                JP NC, @Station.PrintWord.Restore                               ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                EX AF, AF'
Number:         CALL @Station.Print4DigitCore.Entry
                ; восстановление исходного AF' с сохранением основного статуса последнего глифа
Restore:        EX AF, AF'
                POP AF
                EX AF, AF'
                POP DE
                POP HL
                RET

FiveDigits:     EX AF, AF'
                LD H, B
                LD L, C
                ; расчёт цифры десятков тысяч, первое пробное вычитание сразу отделяет 10000..19999
                LD BC, @NumberConst.TwentyThousand
                XOR A
                ADD A, @NumberConst.DigitZero
                SBC HL, BC
                INC A
                JP C, @Station.PrintWord.Remainder                              ; переход, если исходное число не больше 19999, старшая цифра найдена, восстановить остаток

                LD BC, @NumberConst.TenThousand
                SBC HL, BC
                INC A
                JP C, @Station.PrintWord.Remainder                              ; переход, если исходное число не больше 29999, старшая цифра найдена, восстановить остаток

                SBC HL, BC
                INC A
                JP C, @Station.PrintWord.Remainder                              ; переход, если исходное число не больше 39999, старшая цифра найдена, восстановить остаток

                SBC HL, BC
                INC A
                JP C, @Station.PrintWord.Remainder                              ; переход, если исходное число не больше 49999, старшая цифра найдена, восстановить остаток

                SBC HL, BC
                INC A
                JP C, @Station.PrintWord.Remainder                              ; переход, если исходное число не больше 59999, старшая цифра найдена, восстановить остаток

                INC A
                JP @Station.PrintWord.HighDigit

                ; восстановление остатка последнего неудачного вычитания десяти тысяч
Remainder:      LD BC, @NumberConst.TenThousand
                ADD HL, BC
HighDigit:      LD B, H
                LD C, L
                CALL @Station.DrawGlyph.Entry
                JP NC, @Station.PrintWord.Restore                               ; переход, если DrawGlyph отказал в выводе, возврат с его статусом без последующих разрядов

                EX AF, AF'
                ; выбор бюджета четырёх нулей, остаток после старшей цифры обязан занимать четыре разряда
                LD A, #04
                JP @Station.PrintWord.Thousands

                endmodule
                endmodule
