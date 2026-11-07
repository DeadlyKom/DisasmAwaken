                module Action
                module LoadLinkedRecordVectors
                ; Документация [алгоритм и проверка](../../Docs/ActionLinkedVectors.md)
                ; -----------------------------------------
                ; Подготовка двух трёхсловных наборов из связанной записи либо фиксированных значений связи 1A
                ; исходная запись 17, адреса E794..E803
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает доступный LinkedIndex текущей FActionRecord
                ;   операнд RecordPointer по E796 предварительно установлен PrepareLinkedRecordContext, кроме особой связи 1A, которая игнорирует его
                ;   выбранная запись читается по Components и словам 1A, 1C и 1E, первый старший байт этого второго набора задаёт отказ при 80
                ;   ACTION банка 0 выбран, Input0..2 банка 2 и Output0..2 банка 0 доступны для записи, IRQ и повторный вход исключены
                ; Out:
                ;   сначала IY получает RecordPointer, при LinkedIndex=1A он заменяется A780 независимо от подготовленного адреса
                ;   при связи 1A Input0..2 и Output0 равны нулю, Output1=FFB0, Output2=FFFF, HL=FFB0, DE=FFFF, BC=0, AF=1A18
                ;   для остальных связей байт IY.Unknown1B=80 возвращает AF=8041 без изменения HL, DE, BC и всех шести подготовляемых слов
                ;   иначе Input0..2 получают Components выбранного IY, Output0..2 получают слова Unknown1A/1B, Unknown1C/1D и Unknown1E/1F
                ;   на обычном успехе HL=Output1, DE=Output2, BC=Output0, A равен Unknown1B и F соответствует AND A, Carry=0
                ;   HL', DE', BC', AF', IX, I/IM/IFF и paging сохраняются, SP после RET увеличен на два, CPU-стек не записывается
                ;   R добавляет 24 M1 для связи 1A, 11 при отказе и 44 при обычном копировании, бит 7 R сохраняется
                ; Corrupt:
                ;   HL, DE, BC, AF, IY, R, условно Input0..2 и Output0..2, SP внешним RET
                ; Note:
                ;   старший байт Components не проверяется, отказ относится к полному байту Unknown1B второго трёхсловного набора
                ;   прямой вход с исходным нулевым операндом RecordPointer не объявляется допустимым обычным вызовом
                ;   394240 сценариев покрыли полные домены шести слов, все адресные индексы и все байты текущей связи
                ;   сверены точные регистры, флаги, R, восемь банков и все записи, последующее преобразование здесь не исполняется
                ;   общее игровое имя второго набора, полное произведение входов, IRQ, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Чтение ранее подготовленного адреса из изменяемого операнда, исходные нулевые байты инструкции сохранены.
Entry:          LD IY, #0000
                ; Проверка особой связи 1A, её фиксированные наборы не зависят от подготовленной записи.
                LD A, (IX + @FActionRecord.LinkedIndex)
                CP @ActionLinkedVectorsConst.SpecialLink
                JR NZ, @Action.LoadLinkedRecordVectors.ReadRecord               ; переход, если LinkedIndex отличается от 1A, читать два набора выбранной записи

                ; Обнуление трёх входных компонент и первой выходной компоненты для особой связи.
                LD BC, #0000
                LD (@ActionPatchedVectorState.Output0), BC
                LD (@ActionPatchedVectorState.Input0), BC
                LD (@ActionPatchedVectorState.Input1), BC
                LD (@ActionPatchedVectorState.Input2), BC
                ; Подготовка фиксированных Output1=FFB0 и Output2=FFFF, их физические единицы не назначаются.
                LD HL, @ActionLinkedVectorsConst.FixedMiddle
                LD (@ActionPatchedVectorState.Output1), HL
                LD DE, @ActionLinkedVectorsConst.FixedLast
                LD (@ActionPatchedVectorState.Output2), DE
                ; Выбор специального IY=A780 и возврат Carry=0 через AND A.
                LD IY, @ActionLinkedContextConst.SpecialRecord
                AND A
                RET

                ; Проверка старшего байта первого слова второго набора, это Unknown1B, а не Component0.High.
ReadRecord:     LD A, (IY + @FActionRecord.Unknown1B)
                CP @ActionReuseConst.ReusableHigh
                ; Подготовка Carry=1 только для раннего отказа, обычный путь затем очищает его через AND A.
                SCF
                RET Z                                                           ; выход, если Unknown1B выбранной записи равен 80, сохранить шесть прежних подготовленных слов

                ; Установка Carry=0 и смысловых флагов старшего байта на обычном пути подготовки.
                AND A
                ; Подготовка трёх Components выбранной записи в существующие операнды Input0..2.
                LD L, (IY + @FActionRecord.Components.Component0.Low)
                LD H, (IY + @FActionRecord.Components.Component0.High)
                LD (@ActionPatchedVectorState.Input0), HL
                LD L, (IY + @FActionRecord.Components.Component1.Low)
                LD H, (IY + @FActionRecord.Components.Component1.High)
                LD (@ActionPatchedVectorState.Input1), HL
                LD L, (IY + @FActionRecord.Components.Component2.Low)
                LD H, (IY + @FActionRecord.Components.Component2.High)
                LD (@ActionPatchedVectorState.Input2), HL
                ; Подготовка первого слова второго набора, уже прочитанный Unknown1B становится B.
                LD C, (IY + @FActionRecord.Unknown1A)
                LD B, A
                LD (@ActionPatchedVectorState.Output0), BC
                ; Подготовка второго слова второго набора в HL и Output1.
                LD L, (IY + @FActionRecord.Unknown1C)
                LD H, (IY + @FActionRecord.Unknown1D)
                LD (@ActionPatchedVectorState.Output1), HL
                ; Подготовка третьего слова второго набора в DE и Output2.
                LD E, (IY + @FActionRecord.Unknown1E)
                LD D, (IY + @FActionRecord.Unknown1F)
                LD (@ActionPatchedVectorState.Output2), DE
                RET

                endmodule
                endmodule
