                module Action
                module UpdateMotionFromControls
                ; Документация [алгоритм и проверка](../../Docs/ActionMotionVectorTail.md)
                ; -----------------------------------------
                ; Обработка управления и расчёт трёх смещений из знакового слова
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #10A9..#10E8
                ; In:
                ;   SignedWord, коэффициенты C20..C22 и состояние управления доступны, банк 0 выбран
                ;   входные порты и обработчики удовлетворяют договору ScanActionKeys, стек находится в общей RAM
                ; Out:
                ;   после StepNearZeroWord и ScanActionKeys три знаковых масштабированных результата записываются в Component0..2
                ;   IX содержит StoreThird, SP восстанавливается, окончательный RET снимает внешний возврат
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, управление и три слова результата
                ; Note:
                ;   хвост проверен для всех 65536 значений слова, сквозной вариант без клавиш проверен отдельно
                ;   входные и выходные эффекты отдельных клавиатурных обработчиков определяются их договорами
                ; -----------------------------------------
                ; Обработка слова около нуля и опрос клавиатуры перед расчётом смещений.
Entry:          CALL @Action.StepNearZeroWord.Entry
                CALL @Action.ScanActionKeys.Entry
                ; Масштабирование слова первым коэффициентом третьей строки.
ScaleMotion:    LD A, (@ActionPatchedVectorCoeffs.C20)
                NOP
                NOP
                LD DE, (@ActionPanelGaugesState.SignedWord)
                LD IX, @Action.UpdateMotionFromControls.StoreFirst
                JP @Action.MultiplySignedScaled.Entry

StoreFirst:     LD (@ActionScaledVectorState.Component0), HL
                ; Масштабирование того же слова вторым коэффициентом.
                LD A, (@ActionPatchedVectorCoeffs.C21)
                NOP
                NOP
                LD DE, (@ActionPanelGaugesState.SignedWord)
                LD IX, @Action.UpdateMotionFromControls.StoreSecond
                JP @Action.MultiplySignedScaled.Entry

StoreSecond:    LD (@ActionScaledVectorState.Component1), HL
                ; Масштабирование того же слова третьим коэффициентом.
                LD A, (@ActionPatchedVectorCoeffs.C22)
                NOP
                NOP
                LD DE, (@ActionPanelGaugesState.SignedWord)
                LD IX, @Action.UpdateMotionFromControls.StoreThird
                JP @Action.MultiplySignedScaled.Entry

StoreThird:     LD (@ActionScaledVectorState.Component2), HL
                RET

                endmodule
                endmodule
