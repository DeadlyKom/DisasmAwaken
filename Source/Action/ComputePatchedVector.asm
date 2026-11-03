                module Action
                module ComputePatchedVector
                ; Документация [три компоненты и арифметический SP](../../Docs/ActionPatchedVector.md)
                ; -----------------------------------------
                ; Расчёт трёх компонентов по девяти коэффициентам с исходным переносом отрицательных произведений и досрочным выходом по переполнению
                ; исходная запись 17, общая RAM банка 2, адреса AF43..AFF4
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, B сохраняется
                ;   Input0..Input2 существующие изменяемые слова трёх исходных компонентов, девять коэффициентов доступны в окне банка 0
                ;   действует договор MultiplySignedScaled, IX сохраняемый контекст, IY адрес продолжения
                ;   код общей RAM банка 2 и дочерний код банка 0 доступны, повторный вход запрещён, IRQ не вмешиваются при арифметическом SP
                ; Out:
                ;   HL последняя сумма, DE результат последнего MultiplySignedScaled, B сохраняется, C=0
                ;   AF содержит A последнего умножения и F последнего ADC HL,SP, P/V установлен при досрочном выходе по знаковому переполнению
                ;   HL', DE' и BC' сохраняются, AF' от последнего дочернего умножителя, IX восстановлен, IY сохраняется
                ;   SP арифметический накопитель перед последним умножением, входной SP не восстанавливается, PC получает IY
                ;   Output0..Output2 записываются последовательно только после завершения соответствующей строки, старые последующие выходы сохраняются при переполнении
                ;   SavedIX получает входной IX, I, IM и IFF сохраняются, портовых записей и записей по арифметическому SP нет
                ;   R равен сумме стоимостей исполненных детей и исходных переходных ступеней, при полном завершении накладная стоимость 84 M1
                ; Corrupt:
                ;   HL, DE, C, AF, AF', SP, R, SavedIX, от нуля до трёх выходных слов
                ; Note:
                ;   после второго и третьего произведения ADC получает Carry от ребёнка, отрицательное ненулевое произведение добавляет единицу к сумме
                ;   это не обычное матричное произведение с независимым округлением, исходный перенос сохранён
                ;   нет CALL, RET или PUSH при арифметическом SP, вызывающий код обязан восстановить рабочий стек в продолжении IY
                ;   проверены все шесть мест переполнения и исходный коэффициент 80, полный игровой кадр не исполнялся
                ; -----------------------------------------
                ; Сохранение контекста IX в операнд общего выхода, входной SP здесь не сохраняется.
Entry:          LD (@ActionPatchedVectorState.SavedIX), IX
                ; -----------------------------------------
                ; Расчёт компоненты 0 из трёх входных слов
                ; Первое слово читается непосредственно из изменяемого операнда LD DE,n.
                LD DE, #0000
                LD A, (@ActionPatchedVectorCoeffs.C00)
                LD IX, @Action.ComputePatchedVector.NextRow0Term
                JP @Action.MultiplySignedScaled.Entry

                ; Сохранение первого произведения в SP, это арифметическое значение, не адрес CPU-стека.
NextRow0Term:   LD SP, HL
                LD DE, #0000
                LD A, (@ActionPatchedVectorCoeffs.C01)
                LD IX, @Action.ComputePatchedVector.SumRow0Part
                JP @Action.MultiplySignedScaled.Entry

                ; Расчёт суммы первых двух произведений с Carry от последнего умножителя.
SumRow0Part:    ADC HL, SP
                JP PE, @Action.ComputePatchedVector.RestoreIX                   ; переход, если знаковая сумма переполнилась, завершить с сохранением уже записанных компонентов

                ; Сохранение частичной суммы в SP перед третьим произведением.
                LD SP, HL
                LD DE, #0000
                LD A, (@ActionPatchedVectorCoeffs.C02)
                LD IX, @Action.ComputePatchedVector.FinishRow0
                JP @Action.MultiplySignedScaled.Entry

                ; Расчёт полной компоненты 0 с Carry от третьего произведения.
FinishRow0:     ADC HL, SP
                JP PE, @Action.ComputePatchedVector.RestoreIX                   ; переход, если знаковая сумма переполнилась, завершить с сохранением уже записанных компонентов

                ; Обновление Output0 только после обеих успешных проверок знакового переполнения.
                LD (@ActionPatchedVectorState.Output0), HL
                ; -----------------------------------------
                ; Расчёт компоненты 1
                ; Исходные слова читаются из тех же трёх операндов первой строки.
                LD DE, (@ActionPatchedVectorState.Input0)
                LD A, (@ActionPatchedVectorCoeffs.C10)
                LD IX, @Action.ComputePatchedVector.NextRow1Term
                JP @Action.MultiplySignedScaled.Entry

                ; Сохранение первого произведения строки 1 в арифметическом SP.
NextRow1Term:   LD SP, HL
                LD DE, (@ActionPatchedVectorState.Input1)
                LD A, (@ActionPatchedVectorCoeffs.C11)
                LD IX, @Action.ComputePatchedVector.SumRow1Part
                JP @Action.MultiplySignedScaled.Entry

                ; Расчёт частичной суммы строки 1 с исходным Carry ребёнка.
SumRow1Part:    ADC HL, SP
                JP PE, @Action.ComputePatchedVector.RestoreIX                   ; переход, если знаковая сумма переполнилась, завершить с сохранением уже записанных компонентов

                ; Сохранение частичной суммы строки 1 перед последним произведением.
                LD SP, HL
                LD DE, (@ActionPatchedVectorState.Input2)
                LD A, (@ActionPatchedVectorCoeffs.C12)
                LD IX, @Action.ComputePatchedVector.FinishRow1
                JP @Action.MultiplySignedScaled.Entry

                ; Расчёт полной компоненты 1 с исходным Carry ребёнка.
FinishRow1:     ADC HL, SP
                JP PE, @Action.ComputePatchedVector.RestoreIX                   ; переход, если знаковая сумма переполнилась, завершить с сохранением уже записанных компонентов

                ; Обновление Output1, ранее записанный Output0 уже не отменяется.
                LD (@ActionPatchedVectorState.Output1), HL
                ; -----------------------------------------
                ; Расчёт компоненты 2
                LD DE, (@ActionPatchedVectorState.Input0)
                LD A, (@ActionPatchedVectorCoeffs.C20)
                LD IX, @Action.ComputePatchedVector.NextRow2Term
                JP @Action.MultiplySignedScaled.Entry

                ; Сохранение первого произведения строки 2 в арифметическом SP.
NextRow2Term:   LD SP, HL
                LD DE, (@ActionPatchedVectorState.Input1)
                LD A, (@ActionPatchedVectorCoeffs.C21)
                LD IX, @Action.ComputePatchedVector.SumRow2Part
                JP @Action.MultiplySignedScaled.Entry

                ; Расчёт частичной суммы строки 2 с исходным Carry ребёнка.
SumRow2Part:    ADC HL, SP
                JP PE, @Action.ComputePatchedVector.RestoreIX                   ; переход, если знаковая сумма переполнилась, завершить с сохранением уже записанных компонентов

                ; Сохранение частичной суммы строки 2 перед последним произведением.
                LD SP, HL
                LD DE, (@ActionPatchedVectorState.Input2)
                LD A, (@ActionPatchedVectorCoeffs.C22)
                LD IX, @Action.ComputePatchedVector.FinishRow2
                JP @Action.MultiplySignedScaled.Entry

                ; Расчёт полной компоненты 2 с исходным Carry ребёнка.
FinishRow2:     ADC HL, SP
                JP PE, @Action.ComputePatchedVector.RestoreIX                   ; переход, если знаковая сумма переполнилась, завершить с сохранением уже записанных компонентов

                ; Обновление Output2 после завершения всех трёх строк.
                LD (@ActionPatchedVectorState.Output2), HL
                ; -----------------------------------------
                ; Восстановление входного IX и переход в IY
                ; SP остаётся арифметической частичной суммой, восстановление CPU-стека возложено на продолжение.
RestoreIX:      LD IX, #0000
                JP (IY)

                ; -----------------------------------------
                endmodule
                endmodule
