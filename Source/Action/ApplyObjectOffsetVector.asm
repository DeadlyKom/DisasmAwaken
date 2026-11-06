                module Action
                module ApplyObjectOffsetVector
                ; Документация [алгоритм и проверка](../../Docs/ActionObjectOffsetVector.md)
                ; -----------------------------------------
                ; Расчёт трёх базовых слов записи по коэффициентам смещения
                ; исходная запись 17, адреса 6D06..6D37
                ; In:
                ;   DE содержит знаковое слово масштаба, код ACTION и таблицы общей RAM доступны, CPU-стек допускает шесть временных байтов
                ; Out:
                ;   Base0..2 получают результаты трёх настоящих MultiplySignedScaled с одним исходным DE
                ;   HL, DE, BC, AF и AF prime соответствуют последнему произведению, IX восстановлен, IYL получает значение фазовой таблицы
                ;   SP=входной SP+2, I, IM, IFF и страница сохраняются
                ; Corrupt:
                ;   регистры вычислителя, IYL, три операнда коэффициентов, Base0..2 и шесть временных байтов CPU-стека
                ; Note:
                ;   73728 сценариев, включая все исходные DE, сверяют регистры, R и стек, дети исполняются настоящими байтами
                ; -----------------------------------------
                ; Сохранение IX записи и слова масштаба перед расчётом трёх коэффициентов.
Entry:          PUSH IX
                PUSH DE
                CALL @Action.BuildObjectOffsetCoefficients.Entry
                POP DE
                ; Расчёт первого базового слова настоящим MultiplySignedScaled с продолжением через IX.
                LD A, #00
                PUSH DE
                LD IX, @Action.ApplyObjectOffsetVector.Store0
                JP @Action.MultiplySignedScaled.Entry

                ; Запись первого базового слова и повторное использование исходного масштаба.
Store0:         POP DE
                LD (@ActionRecordUpdateState.Base0), HL
                LD A, #00
                PUSH DE
                LD IX, @Action.ApplyObjectOffsetVector.Store1
                JP @Action.MultiplySignedScaled.Entry

                ; Запись второго базового слова и расчёт третьего без дополнительного сохранения DE.
Store1:         POP DE
                LD (@ActionRecordUpdateState.Base1), HL
                LD A, #00
                LD IX, @Action.ApplyObjectOffsetVector.Store2
                JP @Action.MultiplySignedScaled.Entry

                ; Запись третьего базового слова и восстановление указателя записи.
Store2:         LD (@ActionRecordUpdateState.Base2), HL
                POP IX
                RET

                endmodule
                endmodule
