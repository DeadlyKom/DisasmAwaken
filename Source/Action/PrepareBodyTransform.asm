                module Action
                module PrepareBodyTransform
                ; Документация [алгоритм и проверка](../../Docs/ActionPrepareBodyTransform.md)
                ; -----------------------------------------
                ; Подготовка компонент тела и передача арифметическому преобразованию AF43
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #0CAB..#0CE9
                ; In:
                ;   ActionTransformWorkVector.Value задаёт три знаковые 24-битные компоненты, B берётся из BC после девяти LDI
                ;   банк 0 содержит коэффициенты AF43, IX сохраняется, настоящий CPU-стек содержит внешний возврат
                ; Out:
                ;   девять байтов перенесены в записи проекции, младшие байты очищены, Input0..2 получают исходные старшие слова
                ;   SavedSP записан, IY указывает RestoreBodyStack, на входе PublishTransformedBody SP восстановлен и P/V сохраняет итог AF43
                ;   до PublishTransformedBody регистры соответствуют AF43, записанные выходные слова сохраняются и при переполнении
                ; Corrupt:
                ;   компоненты проекции, входные и выходные операнды AF43, SavedSP, IY и рабочие регистры преобразования
                ; Note:
                ;   переход к AF43 выполняется без CALL, арифметический SP не используется для обращений к CPU-стеку
                ;   8846 проходов проверены до входа PublishTransformedBody, отдельная модель проверяет его последующее поведение
                ; -----------------------------------------
                ; Копирование трёх физических 24-битных компонент в рабочие записи проекции.
Entry:          LD HL, @ActionTransformWorkVector.Value
                LD DE, @ActionComponentWork.Component0
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                ; Запись старших слов компонент в три изменяемых входных операнда AF43.
                LD HL, (@ActionComponentWork.Component0.Middle)
                LD (@ActionPatchedVectorState.Input0), HL
                LD HL, (@ActionComponentWork.Component1.Middle)
                LD (@ActionPatchedVectorState.Input1), HL
                LD HL, (@ActionComponentWork.Component2.Middle)
                LD (@ActionPatchedVectorState.Input2), HL
                ; Сохранение настоящего SP до использования регистра как накопителя.
                LD (@ActionRestoreBodyStackState.SavedSP), SP
                ; Очистка младших байтов компонент проекции перед публикацией результатов.
                XOR A
                LD (@ActionComponentWork.Component0.Low), A
                LD (@ActionComponentWork.Component1.Low), A
                LD (@ActionComponentWork.Component2.Low), A
                ; Установка продолжения, которое восстановит CPU-стек после любого выхода AF43.
                LD IY, @Action.RestoreBodyStack.Entry
                JP @Action.ComputePatchedVector.Entry

                endmodule
                endmodule
