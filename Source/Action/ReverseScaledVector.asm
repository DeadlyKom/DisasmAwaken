                module Action
                module ReverseScaledVector
                ; Документация [алгоритм и проверка](../../Docs/ActionVectorReverse.md)
                ; -----------------------------------------
                ; Инвертирование трёх масштабированных компонент и обновление общего знакового слова с разрешением его обработки
                ; исходная запись 17, адреса 6EDE..6F1C
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, DE и BC сохраняются
                ;   Component0, Component1 и Component2 задают три раздельных слова в существующих операндах кода
                ;   ActionPanelGaugesState.SignedWord задаёт исходное общее слово, его полный игровой смысл и единицы ещё не доказаны
                ;   операнды компонент, SignedWord и EnabledCode доступны для записи, банк 0 ACTION выбран, на CPU-стеке внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   Component0, Component2, Component1 последовательно получают своё отрицание по модулю 65536, деления компонент пополам нет
                ;   EnabledCode получает 1, StepNearZeroWord здесь не вызывается
                ;   SignedWord и HL получают arithmetic_shift_right(signed16((-старое слово) mod 65536), 1)+1 по модулю 65536
                ;   DE и BC сохраняются, A инверсия старшего байта исходного SignedWord
                ;   F соответствует последнему RR L до финального INC HL, Carry равен младшему биту исходного SignedWord, флаги не проверяют записанный HL
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2, R получает 44 M1
                ;   RAM получает девять байтовых записей, дополнительных записей CPU-стека и портовых операций нет
                ; Corrupt:
                ;   HL, AF, R, три слова компонент, SignedWord, EnabledCode
                ; Note:
                ;   при исходном SignedWord=8000 отрицание также равно 8000, новый результат C001, замены неограниченной знаковой арифметикой нет
                ;   при старом SignedWord=0 записывается 1, а Z установлен, при старом 1 записывается 0, но Z сброшен
                ;   компоненты меняют только знак сразу, новая величина общего слова попадёт в них лишь при другом последующем вычислении
                ;   связь трёх компонент с SignedWord прослеживается по трём MultiplySignedScaled в 6E6C, полный договор окружающего обработчика ещё не доказан
                ;   обработка близкого объекта по E506 вызывает этот вход, полный игровой смысл события и нативная реакция ещё не подтверждены
                ; -----------------------------------------
                ; Разрешение следующей обработки SignedWord через существующий EnabledCode, самого вызова StepNearZeroWord здесь нет.
Entry:          LD A, #01
                LD (@ActionNearZeroWordState.EnabledCode), A
                ; -----------------------------------------
                ; Инвертирование первой компоненты
                ; Расчёт отрицания Component0 по модулю 65536, величина 8000 остаётся 8000.
                LD HL, (@ActionScaledVectorState.Component0)
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                LD (@ActionScaledVectorState.Component0), HL
                ; -----------------------------------------
                ; Инвертирование третьей компоненты
                ; Расчёт отрицания Component2, исходный физический порядок 0, 2, 1 сохраняется.
                LD HL, (@ActionScaledVectorState.Component2)
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                LD (@ActionScaledVectorState.Component2), HL
                ; -----------------------------------------
                ; Инвертирование второй компоненты
                ; Расчёт отрицания Component1 без изменения её модуля.
                LD HL, (@ActionScaledVectorState.Component1)
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                LD (@ActionScaledVectorState.Component1), HL
                ; -----------------------------------------
                ; Обновление общего знакового слова
                ; Расчёт отрицания SignedWord до сдвига, оборачивание выполняется в пределах слова.
                LD HL, (@ActionPanelGaugesState.SignedWord)
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; Расчёт арифметической половины отрицания с сохранением знакового бита.
                SRA H
                RR L
                ; Обновление результата прибавлением единицы, INC HL не заменяет флаги последнего RR L.
                INC HL
                LD (@ActionPanelGaugesState.SignedWord), HL
                RET

                ; -----------------------------------------
                endmodule
                endmodule
