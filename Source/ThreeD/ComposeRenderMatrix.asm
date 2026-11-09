                module ThreeD
                module ComposeRenderMatrix
                ; Физические поля [заголовок модели](../../Docs/ActionRenderHeaderPhysicalData.md)
                ; Документация [алгоритм и проверка](../../Docs/ThreeDOverlayMirror.md)
                ; -----------------------------------------
                ; Композиция исходной матрицы и ориентации с одноосным режимом и точными четвертями
                ; исходная запись 19, банк 0, смещения #0B23..#0EE2
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, исходные значения сохраняются только по указанным четверть-периодным путям
                ;   ActionPatchedVectorCoeffs.C00..C22 задают девять раздельных исходных байтов сцены
                ;   ActionRenderCoefficientsState.Coeff11..Coeff33 задают матрицу ориентации, подготовленную BuildRenderCoefficients
                ;   бит 0 младшего байта HeaderWord0 по 9B8D выбирает одноосный режим, Phase1 определяет четверть-периодную ветвь
                ;   3DPART доступен в банке 0, страница 98 содержит исходную симметричную таблицу квадратов, IRQ не вмешиваются
                ;   на CPU-стеке находится обычный внешний возврат, дополнительных рамок нет
                ; Out:
                ;   девять выходных операндов Coeff11..Coeff33 получают значения по формулам ActionRenderMatrix.md
                ;   во всех ветвях IY=9B8D, IXL сохраняется, SP после RET равен входному SP+2
                ;   в общем режиме A содержит выходной Coeff33, F относится к его последнему сложению либо коррекции
                ;   в одноосном арифметическом режиме A=C21 исходной матрицы, F=18 OR Carry последнего скорректированного сложения
                ;   в арифметических ветвях BC содержит первые два элемента последнего вычисленного столбца ориентации, D третий элемент, E последний квадрат P
                ;   в арифметических ветвях HL содержит страницу 98 и последний индекс суммы P, IXH последнюю частичную сумму
                ;   в точных четвертях H=98, входной L, DE, BC и IX сохраняются, AF задаётся последней копией либо последним NEG
                ;   для Phase1=0 A=C22 и F=54, для 64 A=C20 и F от NEG C22, для 128 A=-C22 и F от NEG C22, для 192 A=-C20 и F от NEG C20
                ;   HL', DE', BC', AF', I, IM и IFF сохраняются, записи CPU-стека и портовые операции отсутствуют
                ; Corrupt:
                ;   HL, DE, BC, AF, IXH и IY в зависимости от ветви, девять выходных операндов и R
                ; Note:
                ;   дисковая копия слота 19 побайтово совпадает с ACTION по исходным смещениям 6000..801F
                ;   перенос доказательств требует тех же внешней RAM, банка 0, состояния входа и договоров общих процедур вне файла
                ;   нативная загрузка отдельного 3DPART не выполнялась, CF08 сохраняет отдельную неоднозначность исполнения
                ;   общая ветвь корректирует сумму первых двух P, затем отдельно сумму с третьим P, порядок скобок сохраняется
                ;   при одноосном режиме средние члены первых двух столбцов не вычисляются, третий столбец точно копируется из второго столбца сцены
                ;   при одноосном режиме и Phase1, кратной 64, все табличные произведения обходятся точными перестановками и NEG
                ;   NEG исходного 80 оставляет 80, дополнительная коррекция в точных четвертях не выполняется
                ;   выходы являются существующими операндами LD A,n внутри следующего расчёта, отдельная матрица в новой RAM не создаётся
                ;   преобразование вершин, отсечение и вывод после D5C9 не входят в этот локальный договор
                ; -----------------------------------------
                ; -----------------------------------------
                ; Выбор ветви композиции
                ; Подготовка страницы квадратов и указателя на частично неизвестный HeaderWord0.
Entry:          LD H, @ActionProjectionClipConst.SquarePage
                LD IY, @ActionRenderQueueInsertState.HeaderWord0
                ; Проверка бита одной фазы, остальные разряды HeaderWord0 не участвуют в выборе ветви.
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (IY + @FRenderHeaderState.ModeBits)
                JR Z, @ThreeD.ComposeRenderMatrix.Column1                       ; переход, если бит одной фазы сброшен, вычислить общую композицию

                ; Чтение Phase1 и проверка её младших шести разрядов на кратность четверти оборота.
                LD A, (@ActionRenderPhases.Value.Phase1)
                AND @PreviewMatrixComposeConst.QuarterMask
                JP Z, @ThreeD.ComposeRenderMatrix.QuarterTurns                  ; переход, если Phase1 кратна 64, переставить столбцы без табличного округления

                ; -----------------------------------------
                ; Первый столбец результата
                ; Чтение раздельных изменяемых Coeff11, Coeff21 и Coeff31 ориентации в B, C и D.
Column1:        LD B, #00
                LD C, #00
                LD D, #00
                ; Расчёт P(C00, Coeff11) для выходного Coeff11.
                LD A, #00
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Проверка, нужен ли средний член для Coeff11.
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (IY + @FRenderHeaderState.ModeBits)
                JR NZ, @ThreeD.ComposeRenderMatrix.Last11                       ; переход, если бит одной фазы установлен, средний член Coeff11 пропустить

                ; Расчёт P(C01, Coeff21) для выходного Coeff11.
                LD A, #00
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff11.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial11                    ; переход, если сумма Coeff11 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff11 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial11                    ; переход, если NEG суммы Coeff11 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff11, байт 80 превращается в 7F.
                DEC A
Partial11:      LD IXH, A
                ; Расчёт P(C02, Coeff31) для выходного Coeff11.
Last11:         LD A, #00
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff11.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store11                      ; переход, если сумма Coeff11 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff11 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store11                      ; переход, если NEG суммы Coeff11 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff11, байт 80 превращается в 7F.
                DEC A
Store11:        LD (@ActionRenderMatrixState.Coeff11), A
                ; Расчёт P(C10, Coeff11) для выходного Coeff21.
                LD A, #00
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Проверка, нужен ли средний член для Coeff21.
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (IY + @FRenderHeaderState.ModeBits)
                JR NZ, @ThreeD.ComposeRenderMatrix.Last21                       ; переход, если бит одной фазы установлен, средний член Coeff21 пропустить

                ; Расчёт P(C11, Coeff21) для выходного Coeff21.
                LD A, #00
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff21.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial21                    ; переход, если сумма Coeff21 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff21 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial21                    ; переход, если NEG суммы Coeff21 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff21, байт 80 превращается в 7F.
                DEC A
Partial21:      LD IXH, A
                ; Расчёт P(C12, Coeff31) для выходного Coeff21.
Last21:         LD A, #00
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff21.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store21                      ; переход, если сумма Coeff21 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff21 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store21                      ; переход, если NEG суммы Coeff21 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff21, байт 80 превращается в 7F.
                DEC A
Store21:        LD (@ActionRenderMatrixState.Coeff21), A
                ; Расчёт P(C20, Coeff11) для выходного Coeff31.
                LD A, #00
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Проверка, нужен ли средний член для Coeff31.
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (IY + @FRenderHeaderState.ModeBits)
                JR NZ, @ThreeD.ComposeRenderMatrix.Last31                       ; переход, если бит одной фазы установлен, средний член Coeff31 пропустить

                ; Расчёт P(C21, Coeff21) для выходного Coeff31.
                LD A, #00
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff31.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial31                    ; переход, если сумма Coeff31 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff31 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial31                    ; переход, если NEG суммы Coeff31 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff31, байт 80 превращается в 7F.
                DEC A
Partial31:      LD IXH, A
                ; Расчёт P(C22, Coeff31) для выходного Coeff31.
Last31:         LD A, #00
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff31.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store31                      ; переход, если сумма Coeff31 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff31 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store31                      ; переход, если NEG суммы Coeff31 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff31, байт 80 превращается в 7F.
                DEC A
Store31:        LD (@ActionRenderMatrixState.Coeff31), A
                ; -----------------------------------------
                ; Второй столбец результата
                ; Чтение Coeff12, Coeff22 и Coeff32 ориентации для следующих трёх строк.
                LD B, #00
                LD C, #00
                LD D, #00
                ; Расчёт P(C00, Coeff12) для выходного Coeff12.
                LD A, (@ActionPatchedVectorCoeffs.C00)
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Проверка, нужен ли средний член для Coeff12.
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (IY + @FRenderHeaderState.ModeBits)
                JR NZ, @ThreeD.ComposeRenderMatrix.Last12                       ; переход, если бит одной фазы установлен, средний член Coeff12 пропустить

                ; Расчёт P(C01, Coeff22) для выходного Coeff12.
                LD A, (@ActionPatchedVectorCoeffs.C01)
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff12.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial12                    ; переход, если сумма Coeff12 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff12 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial12                    ; переход, если NEG суммы Coeff12 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff12, байт 80 превращается в 7F.
                DEC A
Partial12:      LD IXH, A
                ; Расчёт P(C02, Coeff32) для выходного Coeff12.
Last12:         LD A, (@ActionPatchedVectorCoeffs.C02)
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff12.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store12                      ; переход, если сумма Coeff12 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff12 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store12                      ; переход, если NEG суммы Coeff12 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff12, байт 80 превращается в 7F.
                DEC A
Store12:        LD (@ActionRenderMatrixState.Coeff12), A
                ; Расчёт P(C10, Coeff12) для выходного Coeff22.
                LD A, (@ActionPatchedVectorCoeffs.C10)
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Проверка, нужен ли средний член для Coeff22.
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (IY + @FRenderHeaderState.ModeBits)
                JR NZ, @ThreeD.ComposeRenderMatrix.Last22                       ; переход, если бит одной фазы установлен, средний член Coeff22 пропустить

                ; Расчёт P(C11, Coeff22) для выходного Coeff22.
                LD A, (@ActionPatchedVectorCoeffs.C11)
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff22.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial22                    ; переход, если сумма Coeff22 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff22 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial22                    ; переход, если NEG суммы Coeff22 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff22, байт 80 превращается в 7F.
                DEC A
Partial22:      LD IXH, A
                ; Расчёт P(C12, Coeff32) для выходного Coeff22.
Last22:         LD A, (@ActionPatchedVectorCoeffs.C12)
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff22.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store22                      ; переход, если сумма Coeff22 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff22 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store22                      ; переход, если NEG суммы Coeff22 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff22, байт 80 превращается в 7F.
                DEC A
Store22:        LD (@ActionRenderMatrixState.Coeff22), A
                ; Расчёт P(C20, Coeff12) для выходного Coeff32.
                LD A, (@ActionPatchedVectorCoeffs.C20)
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Проверка, нужен ли средний член для Coeff32.
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (IY + @FRenderHeaderState.ModeBits)
                JR NZ, @ThreeD.ComposeRenderMatrix.Last32                       ; переход, если бит одной фазы установлен, средний член Coeff32 пропустить

                ; Расчёт P(C21, Coeff22) для выходного Coeff32.
                LD A, (@ActionPatchedVectorCoeffs.C21)
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff32.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial32                    ; переход, если сумма Coeff32 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff32 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial32                    ; переход, если NEG суммы Coeff32 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff32, байт 80 превращается в 7F.
                DEC A
Partial32:      LD IXH, A
                ; Расчёт P(C22, Coeff32) для выходного Coeff32.
Last32:         LD A, (@ActionPatchedVectorCoeffs.C22)
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff32.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store32                      ; переход, если сумма Coeff32 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff32 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store32                      ; переход, если NEG суммы Coeff32 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff32, байт 80 превращается в 7F.
                DEC A
Store32:        LD (@ActionRenderMatrixState.Coeff32), A
                ; -----------------------------------------
                ; Третий столбец либо точная копия
                ; Проверка бита одной фазы после первых двух столбцов, BIT сохраняет Carry последней коррекции.
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (IY + @FRenderHeaderState.ModeBits)
                JP NZ, @ThreeD.ComposeRenderMatrix.CopyMiddle                   ; переход, если бит одной фазы установлен, точно скопировать второй столбец сцены

                ; Чтение Coeff13, Coeff23 и Coeff33 ориентации для общего третьего столбца.
                LD B, #00
                LD C, #00
                LD D, #00
                ; Расчёт P(C00, Coeff13) для выходного Coeff13.
                LD A, (@ActionPatchedVectorCoeffs.C00)
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Расчёт P(C01, Coeff23) для выходного Coeff13.
                LD A, (@ActionPatchedVectorCoeffs.C01)
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff13.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial13                    ; переход, если сумма Coeff13 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff13 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial13                    ; переход, если NEG суммы Coeff13 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff13, байт 80 превращается в 7F.
                DEC A
Partial13:      LD IXH, A
                ; Расчёт P(C02, Coeff33) для выходного Coeff13.
                LD A, (@ActionPatchedVectorCoeffs.C02)
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff13.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store13                      ; переход, если сумма Coeff13 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff13 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store13                      ; переход, если NEG суммы Coeff13 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff13, байт 80 превращается в 7F.
                DEC A
Store13:        LD (@ActionRenderMatrixState.Coeff13), A
                ; Расчёт P(C10, Coeff13) для выходного Coeff23.
                LD A, (@ActionPatchedVectorCoeffs.C10)
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Расчёт P(C11, Coeff23) для выходного Coeff23.
                LD A, (@ActionPatchedVectorCoeffs.C11)
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff23.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial23                    ; переход, если сумма Coeff23 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff23 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial23                    ; переход, если NEG суммы Coeff23 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff23, байт 80 превращается в 7F.
                DEC A
Partial23:      LD IXH, A
                ; Расчёт P(C12, Coeff33) для выходного Coeff23.
                LD A, (@ActionPatchedVectorCoeffs.C12)
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff23.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store23                      ; переход, если сумма Coeff23 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff23 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store23                      ; переход, если NEG суммы Coeff23 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff23, байт 80 превращается в 7F.
                DEC A
Store23:        LD (@ActionRenderMatrixState.Coeff23), A
                ; Расчёт P(C20, Coeff13) для выходного Coeff33.
                LD A, (@ActionPatchedVectorCoeffs.C20)
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                ; Расчёт P(C21, Coeff23) для выходного Coeff33.
                LD A, (@ActionPatchedVectorCoeffs.C21)
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы первых двух произведений для Coeff33.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Partial33                    ; переход, если сумма Coeff33 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff33 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Partial33                    ; переход, если NEG суммы Coeff33 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff33, байт 80 превращается в 7F.
                DEC A
Partial33:      LD IXH, A
                ; Расчёт P(C22, Coeff33) для выходного Coeff33.
                LD A, (@ActionPatchedVectorCoeffs.C22)
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт обёрнутой суммы частичного результата и третьего произведения для Coeff33.
                ADD A, IXH
                JP PO, @ThreeD.ComposeRenderMatrix.Store33                      ; переход, если сумма Coeff33 не переполнила signed8, принять её напрямую

                ; Отражение обёрнутого результата Coeff33 через NEG.
                NEG
                JP PO, @ThreeD.ComposeRenderMatrix.Store33                      ; переход, если NEG суммы Coeff33 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff33, байт 80 превращается в 7F.
                DEC A
Store33:        LD (@ActionRenderMatrixState.Coeff33), A
                RET

                ; -----------------------------------------
                ; Точная копия среднего столбца
                ; Копирование C01, C11 и C21 в третий выходной столбец без приближённого P с единичным коэффициентом.
CopyMiddle:     LD A, (@ActionPatchedVectorCoeffs.C01)
                LD (@ActionRenderMatrixState.Coeff13), A
                LD A, (@ActionPatchedVectorCoeffs.C11)
                LD (@ActionRenderMatrixState.Coeff23), A
                LD A, (@ActionPatchedVectorCoeffs.C21)
                LD (@ActionRenderMatrixState.Coeff33), A
                RET

                ; -----------------------------------------
                ; Точные четверти оборота
                ; Копирование второго столбца сцены в третий столбец результата до выбора знаков двух остальных.
QuarterTurns:   LD A, (@ActionPatchedVectorCoeffs.C01)
                LD (@ActionRenderMatrixState.Coeff13), A
                LD A, (@ActionPatchedVectorCoeffs.C11)
                LD (@ActionRenderMatrixState.Coeff23), A
                LD A, (@ActionPatchedVectorCoeffs.C21)
                LD (@ActionRenderMatrixState.Coeff33), A
                ; Чтение полного Phase1, младшие шесть разрядов уже проверены на нуль.
                LD A, (@ActionRenderPhases.Value.Phase1)
                ; Проверка нуля, знака и чётности для различения ровно четырёх возможных фаз.
                AND A
                JR Z, @ThreeD.ComposeRenderMatrix.Quarter0                      ; переход, если Phase1 равна 0, взять первый и третий столбцы сцены

                JP P, @ThreeD.ComposeRenderMatrix.Quarter1                      ; переход, если Phase1 равна 64, взять отрицательный третий и первый столбцы сцены

                JP PO, @ThreeD.ComposeRenderMatrix.Quarter2                     ; переход, если Phase1 равна 128, изменить знаки первого и третьего столбцов сцены

                ; Phase1 равна 192, первый выходной столбец получает третий столбец сцены, второй получает отрицательный первый.
                LD A, (@ActionPatchedVectorCoeffs.C02)
                LD (@ActionRenderMatrixState.Coeff11), A
                LD A, (@ActionPatchedVectorCoeffs.C12)
                LD (@ActionRenderMatrixState.Coeff21), A
                LD A, (@ActionPatchedVectorCoeffs.C22)
                LD (@ActionRenderMatrixState.Coeff31), A
                LD A, (@ActionPatchedVectorCoeffs.C00)
                NEG
                LD (@ActionRenderMatrixState.Coeff12), A
                LD A, (@ActionPatchedVectorCoeffs.C10)
                NEG
                LD (@ActionRenderMatrixState.Coeff22), A
                LD A, (@ActionPatchedVectorCoeffs.C20)
                NEG
                LD (@ActionRenderMatrixState.Coeff32), A
                RET

                ; Phase1 равна 0, первый выходной столбец получает первый столбец сцены, второй получает третий.
Quarter0:       LD A, (@ActionPatchedVectorCoeffs.C00)
                LD (@ActionRenderMatrixState.Coeff11), A
                LD A, (@ActionPatchedVectorCoeffs.C10)
                LD (@ActionRenderMatrixState.Coeff21), A
                LD A, (@ActionPatchedVectorCoeffs.C20)
                LD (@ActionRenderMatrixState.Coeff31), A
                LD A, (@ActionPatchedVectorCoeffs.C02)
                LD (@ActionRenderMatrixState.Coeff12), A
                LD A, (@ActionPatchedVectorCoeffs.C12)
                LD (@ActionRenderMatrixState.Coeff22), A
                LD A, (@ActionPatchedVectorCoeffs.C22)
                LD (@ActionRenderMatrixState.Coeff32), A
                RET

                ; Phase1 равна 64, первый выходной столбец получает отрицательный третий столбец сцены, второй получает первый.
Quarter1:       LD A, (@ActionPatchedVectorCoeffs.C02)
                NEG
                LD (@ActionRenderMatrixState.Coeff11), A
                LD A, (@ActionPatchedVectorCoeffs.C12)
                NEG
                LD (@ActionRenderMatrixState.Coeff21), A
                LD A, (@ActionPatchedVectorCoeffs.C22)
                NEG
                LD (@ActionRenderMatrixState.Coeff31), A
                LD A, (@ActionPatchedVectorCoeffs.C00)
                LD (@ActionRenderMatrixState.Coeff12), A
                LD A, (@ActionPatchedVectorCoeffs.C10)
                LD (@ActionRenderMatrixState.Coeff22), A
                LD A, (@ActionPatchedVectorCoeffs.C20)
                LD (@ActionRenderMatrixState.Coeff32), A
                RET

                ; Phase1 равна 128, первый и третий столбцы сцены копируются с отрицанием.
Quarter2:       LD A, (@ActionPatchedVectorCoeffs.C00)
                NEG
                LD (@ActionRenderMatrixState.Coeff11), A
                LD A, (@ActionPatchedVectorCoeffs.C10)
                NEG
                LD (@ActionRenderMatrixState.Coeff21), A
                LD A, (@ActionPatchedVectorCoeffs.C20)
                NEG
                LD (@ActionRenderMatrixState.Coeff31), A
                LD A, (@ActionPatchedVectorCoeffs.C02)
                NEG
                LD (@ActionRenderMatrixState.Coeff12), A
                LD A, (@ActionPatchedVectorCoeffs.C12)
                NEG
                LD (@ActionRenderMatrixState.Coeff22), A
                LD A, (@ActionPatchedVectorCoeffs.C22)
                NEG
                LD (@ActionRenderMatrixState.Coeff32), A
                RET

                ; -----------------------------------------
                endmodule
                endmodule
