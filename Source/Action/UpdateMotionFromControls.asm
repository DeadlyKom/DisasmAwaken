                module Action
                module UpdateMotionFromControls
                ; Документация [алгоритм и проверка](../../Docs/ActionMotionVectorTail.md)
                ; -----------------------------------------
                ; Обработка управления и расчёт трёх смещений из знакового слова
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #10A9..#10E8
                ; In:
                ;   SignedWord, коэффициенты C20..C22 и состояние управления доступны, банк 0 выбран, пары направления согласованы как 0000 либо ED44
                ;   входные порты и обработчики удовлетворяют договору ScanActionKeys, стек находится в общей RAM
                ; Out:
                ;   при MotionOpcode=3A после двух первых вызовов Component0..2 получают произведения SignedWord на эффективные коэффициенты C20..C22
                ;   для пар 0000 коэффициент не меняется, для ED44 берётся его восьмибитное отрицание, исходное 80 остаётся 80
                ;   при MotionOpcode=3A IX содержит StoreThird, SP восстанавливается, окончательный RET снимает внешний возврат
                ;   при MotionOpcode=C9 после двух первых вызовов следует RET без пересчёта Component0..2, IX и регистры остаются от вызываемых процедур
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, управление и три слова результата
                ; Note:
                ;   хвост с исходным опкодом 3A проверен для всех 65536 значений слова, сквозной вариант без клавиш проверен отдельно
                ;   входные и выходные эффекты отдельных клавиатурных обработчиков определяются их договорами
                ;   произвольный опкод не покрывается договором, [команда свободного полёта](../../Docs/ActionFreeFlightCommand.md) записывает только 3A или C9
                ;   [переключатель вида](../../Docs/ActionViewDirectionCommand.md) создаёт три согласованные пары, задний хвост проверен отдельно на всех 65536 словах
                ; -----------------------------------------
                ; Обработка слова около нуля и опрос клавиатуры перед расчётом смещений.
Entry:          CALL @Action.StepNearZeroWord.Entry
                CALL @Action.ScanActionKeys.Entry
                ; Масштабирование слова первым коэффициентом третьей строки.
ScaleMotion:    LD A, (@ActionPatchedVectorCoeffs.C20)
                ; Пара изменяемого кода, 0000 даёт две NOP, ED44 даёт NEG загруженного коэффициента.
NegateFirst:    NOP
                NOP
                LD DE, (@ActionPanelGaugesState.SignedWord)
                LD IX, @Action.UpdateMotionFromControls.StoreFirst
                JP @Action.MultiplySignedScaled.Entry

StoreFirst:     LD (@ActionScaledVectorState.Component0), HL
                ; Масштабирование того же слова вторым коэффициентом.
                LD A, (@ActionPatchedVectorCoeffs.C21)
                ; Пара изменяемого кода, 0000 даёт две NOP, ED44 даёт NEG загруженного коэффициента.
NegateSecond:   NOP
                NOP
                LD DE, (@ActionPanelGaugesState.SignedWord)
                LD IX, @Action.UpdateMotionFromControls.StoreSecond
                JP @Action.MultiplySignedScaled.Entry

StoreSecond:    LD (@ActionScaledVectorState.Component1), HL
                ; Масштабирование того же слова третьим коэффициентом.
                LD A, (@ActionPatchedVectorCoeffs.C22)
                ; Пара изменяемого кода, 0000 даёт две NOP, ED44 даёт NEG загруженного коэффициента.
NegateThird:    NOP
                NOP
                LD DE, (@ActionPanelGaugesState.SignedWord)
                LD IX, @Action.UpdateMotionFromControls.StoreThird
                JP @Action.MultiplySignedScaled.Entry

StoreThird:     LD (@ActionScaledVectorState.Component2), HL
                RET

                endmodule
                endmodule
