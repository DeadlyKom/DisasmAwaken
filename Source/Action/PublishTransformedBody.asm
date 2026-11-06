                module Action
                module PublishTransformedBody
                ; Документация [алгоритм и проверка](../../Docs/ActionPrepareBodyTransform.md)
                ; -----------------------------------------
                ; Публикация знаковых компонент, подготовка проекции и рисование преобразованного тела
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #0CED..#0D52
                ; In:
                ;   настоящий CPU-стек уже восстановлен, P/V задаёт результат AF43, три выхода AF43 находятся в банке 0
                ;   младшие байты компонент проекции подготовлены, 7FFD доступен для переключения, CPU-стек допускает двадцать временных байтов
                ; Out:
                ;   при P/V=1 выполняется немедленный RET с сохранением регистров, RAM и страницы, SP=входной SP+2
                ;   иначе старшие знаковые байты выходов записаны в First.X, First.Y и First.SignSource до преобразований
                ;   знаковые слова преобразованы к знаку и модулю, вторая компонента предварительно отрицается по модулю 65536
                ;   при FirstMode=2 Pattern=00FF, иначе Pattern=0000, 7FFD получает 11 и 10, A=10, F соответствует проекции и рисованию
                ; Corrupt:
                ;   регистры и память ProjectAndDrawBody, поля первого значка, верхние слова компонент, 7FFD и временная рамка
                ; Note:
                ;   37727 сценариев включают все входные AF с P/V=1, настоящую проекцию и оба профиля рисунка
                ;   проверены регистры кроме R, RAM и OUT, содержимое внутренней рамки проекции имеет отдельное ограничение
                ; -----------------------------------------
Entry:          RET PE                                                          ; выход, если AF43 обнаружил знаковое переполнение, пропустить публикацию и рисование

                ; Сохранение знакового старшего байта X и преобразование слова в знак и модуль.
                LD HL, (@ActionPatchedVectorState.Output0)
                LD A, H
                LD (@ActionGlyphIndicatorState.First.X), A
                BIT 7, H
                JR Z, @Action.PublishTransformedBody.StoreX                     ; переход, если X неотрицателен, записать исходное слово

                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SET 7, H
StoreX:         LD (@ActionComponentWork.Component0.Middle), HL
                ; Сохранение знакового старшего байта Y до инверсии направления и упаковки.
                LD HL, (@ActionPatchedVectorState.Output1)
                LD A, H
                LD (@ActionGlyphIndicatorState.First.Y), A
                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                INC HL
                BIT 7, H
                JR Z, @Action.PublishTransformedBody.StoreY                     ; переход, если инвертированный Y неотрицателен, записать его без дополнительного отрицания

                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SET 7, H
StoreY:         LD (@ActionComponentWork.Component1.Middle), HL
                ; Сохранение знакового старшего байта глубины и преобразование её слова.
                LD HL, (@ActionPatchedVectorState.Output2)
                LD A, H
                LD (@ActionGlyphIndicatorState.First.SignSource), A
                BIT 7, H
                JR Z, @Action.PublishTransformedBody.StoreDepth                 ; переход, если глубина неотрицательна, записать исходное слово

                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SET 7, H
StoreDepth:     LD (@ActionComponentWork.Component2.Middle), HL
                ; Проверка FirstMode для выбора сплошной заливки.
                LD A, (@ActionGlyphIndicatorState.Control.FirstMode)
                CP #02
                LD DE, #0000
                JR NZ, @Action.PublishTransformedBody.SelectControls            ; переход, если FirstMode не равен 2, сохранить нулевой рисунок

                LD E, #FF
                ; Подключение CONTROL и вызов проекции с выбранным рисунком.
SelectControls: LD A, @ActionBankPage.Controls
                CALL @Action.SelectMemoryPage.Entry
                CALL @Controls.ProjectAndDrawBody.Entry
                ; Возврат ACTION после проекции и возможного рисования.
                LD A, @ActionBankPage.Runtime
                CALL @Action.SelectMemoryPage.Entry
                RET

                endmodule
                endmodule
