                module Action
                module BuildRenderCoefficients
                ; Документация [точные формулы коэффициентов](../../Docs/ActionRenderCoefficients.md)
                ; -----------------------------------------
                ; Построение девяти байтовых коэффициентов по трём фазам либо по одной фазе
                ; исходная запись 17, код ACTION банка 0, адреса C99B..CB22
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, входные флаги на результаты не влияют
                ;   Phase0, Phase1 и Phase2 по 9B12..9B14 задают три байтовых индекса исходной синусоиды, оборот равен 256
                ;   бит 0 младшего байта HeaderWord0 по 9B8D выбирает короткий режим, остальные семь разрядов здесь не проверяются
                ;   ACTION доступен в банке 0, страницы 98 и 99 содержат исходные таблицы квадратов и синусоиды
                ;   на CPU-стеке находится внешний возврат, дополнительных рамок нет, IRQ не вмешиваются
                ; Out:
                ;   девять раздельных операндов Coeff11..Coeff33 получают значения по точным байтовым формулам ActionRenderCoefficients.md
                ;   при бите 0 равном 1 используются только Phase1, HL=9900 OR Phase1, B=Phase1, C и DE сохраняются, AF=7F44
                ;   в коротком режиме IX и IY сохраняются, Coeff11=Coeff32=cos Phase1, Coeff12=sin Phase1, Coeff31=-sin Phase1
                ;   в коротком режиме Coeff13, Coeff21, Coeff22, Coeff33 равны нулю, Coeff23=127
                ;   в общем режиме BC содержит sin Phase0 и cos Phase0, IX содержит P(cos Phase1,cos Phase0) и sin Phase1
                ;   в общем режиме IY содержит cos Phase2 и cos Phase1, HL содержит страницу 98 и последний индекс P(P(sin Phase1,sin Phase0),sin Phase2)
                ;   в общем режиме D=sin Phase2, E содержит последний квадрат по первому индексу P, A=Coeff32, F относится к последнему сложению либо его коррекции
                ;   HL', DE', BC', AF', I, IM и IFF сохраняются, SP после RET равен входному SP+2, портов и дополнительных записей стека нет
                ; Corrupt:
                ;   HL, DE, BC, AF, IX и IY по общему пути, HL, B и AF по короткому пути, девять операндов коэффициентов и R
                ; Note:
                ;   P использует signed8-половины с округлением вниз и два байтовых индекса свёрнутой таблицы, обычным произведением не заменяется
                ;   при Overflow сложения либо вычитания выполняется NEG обёрнутого результата, при Overflow NEG выполняется DEC, это не обычное насыщение
                ;   режим одной фазы не проверяет нулевые Phase0 и Phase2, их значения просто игнорируются
                ;   все девять коэффициентов являются раздельными непосредственными операндами, непрерывная фиктивная структура матрицы не создаётся
                ;   записи UpdateFrame при выбранном банке 4 по совпадающим адресам относятся к OBJECT3D и не изменяют этот код банка 0
                ;   матрица предварительного просмотра имеет те же числовые примитивы, однако байты и регистры ACTION проверены отдельно по своему образу
                ;   композиция CB23 проверена отдельно, преобразование вершин ещё не доказано, этот договор ограничен C99B..CB22
                ; -----------------------------------------
                ; -----------------------------------------
                ; Выбор режима коэффициентов
                ; Проверка бита одной фазы в младшем байте HeaderWord0, прочие разряды здесь не интерпретируются.
                ; Младший байт HeaderWord0, разряды 7..0, ? ? ? ? ? ? ? S, маска S равна 01.
                ; S=1 выбирает одну фазу, нулевой байт выбирает общий расчёт, остальные биты неизвестны.
Entry:          LD HL, @ActionRenderQueueInsertState.HeaderWord0
                BIT @ActionRenderCoefficientsConst.OneAxisBit, (HL)
                JR Z, @Action.BuildRenderCoefficients.ThreePhases               ; переход, если бит одной фазы сброшен, использовать три исходные фазы

                ; Чтение Phase1 для короткого режима, Phase0 и Phase2 не используются.
                LD A, (@ActionRenderPhases.Value.Phase1)
                LD B, A
                ; Расчёт четверть-периодного индекса косинуса Phase1 по модулю 256.
                ADD A, @BufferPointMotionConst.QuarterCycle
                LD H, @BufferPointMotionConst.SinePage
                LD L, A
                ; Сохранение одинакового косинуса в Coeff11 и Coeff32.
                LD A, (HL)
                LD (@ActionRenderCoefficientsState.Coeff11), A
                LD (@ActionRenderCoefficientsState.Coeff32), A
                ; Чтение исходного синуса Phase1 для Coeff12.
                LD L, B
                LD A, (HL)
                LD (@ActionRenderCoefficientsState.Coeff12), A
                ; Расчёт отрицательного синуса для Coeff31 по модулю 256.
                NEG
                LD (@ActionRenderCoefficientsState.Coeff31), A
                ; Обнуление четырёх коэффициентов короткого режима, единичный Coeff23 равен 127.
                XOR A
                LD (@ActionRenderCoefficientsState.Coeff13), A
                LD (@ActionRenderCoefficientsState.Coeff21), A
                LD (@ActionRenderCoefficientsState.Coeff22), A
                LD (@ActionRenderCoefficientsState.Coeff33), A
                LD A, @ActionRenderCoefficientsConst.Unit
                LD (@ActionRenderCoefficientsState.Coeff23), A
                RET

                ; -----------------------------------------
                ; Подготовка трёх фаз
                ; Чтение синуса и четверть-периодной выборки Phase0 в B и C.
ThreePhases:    LD A, (@ActionRenderPhases.Value.Phase0)
                LD H, @BufferPointMotionConst.SinePage
                LD L, A
                LD B, (HL)
                ; Расчёт индекса косинуса Phase0 с байтовым оборачиванием.
                ADD A, @BufferPointMotionConst.QuarterCycle
                LD L, A
                LD C, (HL)
                ; Чтение синуса Phase1 в IXL.
                LD A, (@ActionRenderPhases.Value.Phase1)
                LD L, A
                LD A, (HL)
                LD IXL, A
                ; Расчёт индекса косинуса Phase1, результат выборки сохраняется в IYL.
                LD A, L
                ADD A, @BufferPointMotionConst.QuarterCycle
                LD L, A
                LD A, (HL)
                LD IYL, A
                ; Чтение синуса Phase2 в D и запись его отрицания в Coeff13.
                LD A, (@ActionRenderPhases.Value.Phase2)
                LD L, A
                LD A, (HL)
                LD D, A
                ; Расчёт отрицательного sin Phase2 по модулю 256.
                NEG
                LD (@ActionRenderCoefficientsState.Coeff13), A
                ; Расчёт четверть-периодной выборки Phase2 для IYH.
                LD A, L
                ADD A, @BufferPointMotionConst.QuarterCycle
                LD L, A
                LD A, (HL)
                LD IYH, A
                ; -----------------------------------------
                ; Табличные произведения
                ; Подготовка страницы квадратов и пары cos Phase2, cos Phase1 для Coeff11.
                LD H, @ActionProjectionClipConst.SquarePage
                LD E, IYL
                ; Расчёт P(cos Phase2, cos Phase1) через разность двух свёрнутых квадратов.
                SRA A
                LD L, E
                SRA L
                SUB L
                LD L, A
                ADD A, E
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD (@ActionRenderCoefficientsState.Coeff11), A
                ; Расчёт P(sin Phase1, cos Phase2) для Coeff12.
                LD A, IXL
                LD E, IYH
                SRA A
                LD L, E
                SRA L
                SUB L
                LD L, A
                ADD A, E
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD (@ActionRenderCoefficientsState.Coeff12), A
                ; Расчёт P(sin Phase1, sin Phase0), временное значение сохраняется в IXH.
                LD A, IXL
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
                ; Расчёт P(cos Phase1, cos Phase0), затем произведения результата с sin Phase2.
                LD A, IYL
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
                ; Расчёт внешнего произведения с sin Phase2 для Coeff21.
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
                ; Расчёт суммы двух табличных членов Coeff21 и проверка знакового переполнения.
                ADD A, IXH
                JP PO, @Action.BuildRenderCoefficients.StoreCoeff21             ; переход, если сумма Coeff21 не переполнила signed8, сохранить её напрямую

                ; Отражение обёрнутой суммы Coeff21 через NEG, результат 80 требует отдельного DEC.
                NEG
                JP PO, @Action.BuildRenderCoefficients.StoreCoeff21             ; переход, если NEG суммы Coeff21 не переполнился, дополнительный DEC не нужен

                ; Коррекция единственного повторного Overflow, байт 80 превращается в 7F.
                DEC A
StoreCoeff21:   LD (@ActionRenderCoefficientsState.Coeff21), A
                ; Расчёт P(cos Phase2, cos Phase0) для Coeff23.
                LD A, IYH
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
                LD (@ActionRenderCoefficientsState.Coeff23), A
                ; Расчёт P(cos Phase1, sin Phase0), временное значение сохраняется в IXH.
                LD A, IYL
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
                ; Расчёт P(sin Phase1, cos Phase0) для внешнего произведения Coeff22.
                LD A, IXL
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
                ; Расчёт P полученного байта с sin Phase2.
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
                ; Расчёт разности двух членов Coeff22 и проверка Overflow.
                SUB IXH
                JP PO, @Action.BuildRenderCoefficients.StoreCoeff22             ; переход, если разность Coeff22 не переполнила signed8, сохранить её напрямую

                ; Отражение обёрнутой разности Coeff22 через NEG.
                NEG
                JP PO, @Action.BuildRenderCoefficients.StoreCoeff22             ; переход, если NEG разности Coeff22 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff22, байт 80 превращается в 7F.
                DEC A
StoreCoeff22:   LD (@ActionRenderCoefficientsState.Coeff22), A
                ; Расчёт P(sin Phase1, cos Phase0), временное значение для Coeff31 сохраняется в IXH.
                LD A, IXL
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
                LD IXH, A
                ; Расчёт P(cos Phase1, sin Phase0) перед внешним произведением с sin Phase2.
                LD A, IYL
ScaleCoeff31:   SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ; Расчёт внешнего произведения с sin Phase2 для Coeff31.
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
                ; Расчёт разности двух членов Coeff31 и проверка Overflow.
                SUB IXH
                JP PO, @Action.BuildRenderCoefficients.StoreCoeff31             ; переход, если разность Coeff31 не переполнила signed8, сохранить её напрямую

                ; Отражение обёрнутой разности Coeff31 через NEG.
                NEG
                JP PO, @Action.BuildRenderCoefficients.StoreCoeff31             ; переход, если NEG разности Coeff31 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff31, байт 80 превращается в 7F.
                DEC A
StoreCoeff31:   LD (@ActionRenderCoefficientsState.Coeff31), A
                ; Расчёт P(cos Phase2, sin Phase0) для Coeff33.
                LD A, IYH
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
ReadCoeff33Base:LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD (@ActionRenderCoefficientsState.Coeff33), A
                ; Расчёт P(cos Phase1, cos Phase0), последнее временное значение в IXH.
                LD A, IYL
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
                LD IXH, A
                ; Расчёт P(sin Phase1, sin Phase0) перед внешним произведением Coeff32.
                LD A, IXL
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
                ; Расчёт внешнего произведения с sin Phase2 для Coeff32.
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
                ; Расчёт суммы двух членов Coeff32, её флаги либо флаги коррекции остаются на выходе процедуры.
                ADD A, IXH
                JP PO, @Action.BuildRenderCoefficients.StoreCoeff32             ; переход, если сумма Coeff32 не переполнила signed8, сохранить её напрямую

                ; Отражение обёрнутой суммы Coeff32 через NEG.
                NEG
                JP PO, @Action.BuildRenderCoefficients.StoreCoeff32             ; переход, если NEG суммы Coeff32 не переполнился, DEC пропустить

                ; Коррекция повторного Overflow Coeff32, байт 80 превращается в 7F.
                DEC A
StoreCoeff32:   LD (@ActionRenderCoefficientsState.Coeff32), A
                RET

                ; -----------------------------------------
                endmodule
                endmodule
