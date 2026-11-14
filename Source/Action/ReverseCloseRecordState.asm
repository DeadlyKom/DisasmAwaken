                module Action
                module ReverseCloseRecordState
                ; Документация [три входа обработки записи](../../Docs/ActionCloseRecord.md)
                ; -----------------------------------------
                ; Уменьшение кода запрета, инвертирование масштабированных компонент и особое обнуление состояния класса 12
                ; исходная запись 17, код ACTION банка 0, адреса E54A..E55B
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, DE и BC сохраняются, IX адрес читаемой FActionRecord
                ;   InhibitCode задаёт исходный полный байт, ClassCode определяет дополнительное обнуление FirstValue
                ;   действует договор ReverseScaledVector, состояние доступно для записи, банк 0 выбран, два дополнительных байта CPU-стека доступны, IRQ не вмешиваются
                ; Out:
                ;   InhibitCode уменьшается на один по модулю 256, входной 00 превращается в FF
                ;   Component0, Component2, Component1 меняют знак, SpeedWord обновляется по договору ReverseScaledVector, EnabledCode получает 1
                ;   HL новое SpeedWord, DE и BC сохраняются, при классе не 12 A=ClassCode и F от CP с 12
                ;   при классе 12 FirstValue получает 0 и AF=0044, это условие не заменяется корневым переходом в другой режим
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2, OUT отсутствуют
                ;   R получает 51 M1 для классов не 12 и 54 M1 для класса 12
                ; Corrupt:
                ;   HL, AF, R, два байта временного CPU-стека, InhibitCode, три компоненты, SpeedWord, EnabledCode, FirstValue только при классе 12
                ; Note:
                ;   InhibitCode уменьшается косвенным DEC (HL), писатель существующего операнда по E507 зарегистрирован отдельно
                ;   FirstValue читается при выводе первой шкалы, условие обнуления по классу 12 установлено точно
                ; -----------------------------------------
                ; Уменьшение полного InhibitCode по модулю байта, исходное 00 получает FF.
Entry:          LD HL, @ActionCloseRecordState.InhibitCode
                DEC (HL)
                ; Инвертирование масштабированных компонент и отдельное обновление SpeedWord настоящим дочерним вызовом.
                CALL @Action.ReverseScaledVector.Entry
                ; Проверка ClassCode после инверсии, только класс 12 дополнительно обнуляет FirstValue.
                LD A, (IX + FActionRecord.ClassCode)
                CP @ActionCloseRecordConst.TransferClass
                RET NZ                                                          ; выход, если ClassCode не равен 12, FirstValue сохранить

                ; Обнуление значения первой шкалы FirstValue для класса 12 и формирование AF=0044.
                XOR A
                LD (@ActionPanelGaugesState.FirstValue), A
                RET

                endmodule
                endmodule
