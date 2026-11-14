                module Text
                module ReadDecimal5
                ; Документация [Text](../../Docs/FunctionDetails/Text.md)
                ; Подробный разбор [ScriptLanguage.md](../../Docs/ScriptLanguage.md)
                ; -----------------------------------------
                ; Чтение от одной до пяти ASCII-цифр, десятичное число в HL по модулю 65536
                ; исходная запись 5, файловые смещения #06EA..#079B
                ; In:
                ;   IX - первая десятичная ASCII-цифра, наличие первой цифры проверяет вызывающий код
                ; Out:
                ;   HL - значение от одной до пяти цифр по модулю 65536
                ;   DE сохраняется при одной цифре, при двух и более содержит число из всех цифр кроме первой
                ;   BC - B=0, C сохраняется при одной цифре, равен удвоенной первой цифре при двух, первой цифре при трёх и более
                ;   AF - A равен первой цифре при одной и пяти цифрах, при двух, трёх и четырёх равен 1
                ;   IX - первый непрочитанный символ
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, R
                ; Note:
                ;   последняя временная пара содержит удвоенную цифру десятков для двух цифр, для трёх и более содержит первую цифру
                ;   при двух и более цифрах PUSH записывает два байта ниже входного SP, POP не стирает записанные байты
                ;   все разряды повторно используют ту же пару стековых байтов, при одной цифре записей в RAM нет
                ;   кроме временного стека RAM не меняется, обычный RET даёт SP на два больше входного
                ;   пять цифр завершают чтение без проверки шестой, ведущие нули допустимы
                ;   десятичные разряды складываются без насыщения, 99999 возвращает 34463
                ;   альтернативные регистры и IY сохраняются, SP восстанавливается, проверки ошибок первой цифры нет
                ; -----------------------------------------
                ; переход за уже проверенную первую цифру перед поиском конца числа
Entry:          INC IX
                LD A, (IX + @ScriptConst.Cursor)
                LD B, #01
                ; проверка нижней границы десятичной цифры в следующем символе
                CP @ScriptConst.DecimalZero
                JR C, @Text.ReadDecimal5.ConvertDigits                          ; переход, если следующий символ меньше кода цифры ноль, чтение числа завершено

                ; проверка верхней границы десятичной цифры в следующем символе
                CP @ScriptConst.DecimalLimit
                JR NC, @Text.ReadDecimal5.ConvertDigits                         ; переход, если следующий символ больше кода цифры девять, чтение числа завершено

                INC IX
                LD A, (IX + @ScriptConst.Cursor)
                INC B
                ; проверка нижней границы десятичной цифры в следующем символе
                CP @ScriptConst.DecimalZero
                JR C, @Text.ReadDecimal5.ConvertDigits                          ; переход, если следующий символ меньше кода цифры ноль, чтение числа завершено

                ; проверка верхней границы десятичной цифры в следующем символе
                CP @ScriptConst.DecimalLimit
                JR NC, @Text.ReadDecimal5.ConvertDigits                         ; переход, если следующий символ больше кода цифры девять, чтение числа завершено

                INC IX
                LD A, (IX + @ScriptConst.Cursor)
                INC B
                ; проверка нижней границы десятичной цифры в следующем символе
                CP @ScriptConst.DecimalZero
                JR C, @Text.ReadDecimal5.ConvertDigits                          ; переход, если следующий символ меньше кода цифры ноль, чтение числа завершено

                ; проверка верхней границы десятичной цифры в следующем символе
                CP @ScriptConst.DecimalLimit
                JR NC, @Text.ReadDecimal5.ConvertDigits                         ; переход, если следующий символ больше кода цифры девять, чтение числа завершено

                INC IX
                LD A, (IX + @ScriptConst.Cursor)
                INC B
                ; проверка нижней границы десятичной цифры в следующем символе
                CP @ScriptConst.DecimalZero
                JR C, @Text.ReadDecimal5.ConvertDigits                          ; переход, если следующий символ меньше кода цифры ноль, чтение числа завершено

                ; проверка верхней границы десятичной цифры в следующем символе
                CP @ScriptConst.DecimalLimit
                JR NC, @Text.ReadDecimal5.ConvertDigits                         ; переход, если следующий символ больше кода цифры девять, чтение числа завершено

                INC B
                INC IX
                ; преобразование последней прочитанной цифры в единицы результата
ConvertDigits:  LD A, (IX - @ScriptConst.UnitsBack)
                SUB @ScriptConst.DecimalZero
                LD L, A
                LD H, #00
                DJNZ @Text.ReadDecimal5.AddTens

                RET

                ; расчёт вклада десятков, цифра умножается на 10 и добавляется к единицам
AddTens:        EX DE, HL
                LD A, (IX - @ScriptConst.TensBack)
                SUB @ScriptConst.DecimalZero
                LD L, A
                LD A, B
                LD H, #00
                ADD HL, HL
                PUSH HL
                ADD HL, HL
                ADD HL, HL
                POP BC
                ADD HL, BC
                ADD HL, DE
                LD B, A
                DJNZ @Text.ReadDecimal5.AddHundreds

                RET

                ; расчёт вклада сотен, цифра умножается на 100 и добавляется к младшим разрядам
AddHundreds:    EX DE, HL
                LD A, (IX - @ScriptConst.HundredsBack)
                SUB @ScriptConst.DecimalZero
                LD L, A
                LD A, B
                LD H, #00
                PUSH HL
                ADD HL, HL
                POP BC
                ADD HL, BC
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, HL
                ADD HL, DE
                LD B, A
                DJNZ @Text.ReadDecimal5.AddThousands

                RET

                ; расчёт вклада тысяч, промежуточные суммы дают множитель 1000
AddThousands:   EX DE, HL
                LD A, (IX - @ScriptConst.ThousandsBack)
                SUB @ScriptConst.DecimalZero
                LD L, A
                LD A, B
                LD H, #00
                PUSH HL
                ADD HL, HL
                POP BC
                ADD HL, BC
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, DE
                LD B, A
                DJNZ @Text.ReadDecimal5.AddTenThousands

                RET

                ; расчёт вклада десятков тысяч, переполнение 16-битной суммы сохраняется как в оригинале
AddTenThousands:EX DE, HL
                LD A, (IX - @ScriptConst.TenThousands)
                SUB @ScriptConst.DecimalZero
                LD L, A
                LD H, #00
                PUSH HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                POP BC
                ADD HL, BC
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, BC
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, DE
                RET

                endmodule
                endmodule
