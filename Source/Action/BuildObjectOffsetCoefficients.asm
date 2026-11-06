                module Action
                module BuildObjectOffsetCoefficients
                ; Документация [алгоритм и проверка](../../Docs/ActionObjectOffsetCoefficients.md)
                ; -----------------------------------------
                ; Подготовка коэффициентов смещения по трём фазовым парам
                ; исходная запись 17, адреса B044..B0E8
                ; In:
                ;   Offset0..2 задают три байтовых индекса, фазовая страница 9900 и таблица квадратов 9800 доступны
                ; Out:
                ;   Coefficient0..2 получают три числовых коэффициента, BC содержит первую фазовую пару, IX и IYL содержат рабочие значения
                ;   HL и DE содержат адрес и данные последней разности, AF возвращает третий коэффициент и его флаги
                ;   SP=входной SP+2, записи выполняются только в три операнда
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, IYL, R и три операнда
                ; Note:
                ;   арифметические деления байтов на два и разности таблицы сохраняют оборачивание
                ;   переполнение второй и третьей разности исправляется исходным NEG, результат 80 после NEG уменьшается до 7F
                ;   8192 самостоятельных сценария и композиционная проверка обёртки подтверждают точные регистры и записи
                ; -----------------------------------------
                ; Чтение трёх фазовых пар, второй элемент каждой находится на 64 позиции дальше по модулю байта.
Entry:          LD A, #00
                LD H, @ActionObjectOffsetConst.PhasePage
                LD L, A
                LD B, (HL)
                ADD A, @ActionObjectOffsetConst.PhaseStep
                LD L, A
                LD C, (HL)
                LD A, #00
                LD L, A
                LD A, (HL)
                LD IXL, A
                LD A, L
                ADD A, @ActionObjectOffsetConst.PhaseStep
                LD L, A
                LD A, (HL)
                LD IYL, A
                LD A, #00
                LD L, A
                LD A, (HL)
                LD D, A
                LD A, L
                ADD A, @ActionObjectOffsetConst.PhaseStep
                LD L, A
                LD E, (HL)
                ; Расчёт первого коэффициента через разность табличных квадратов.
                LD H, @ActionObjectOffsetConst.SquarePage
                LD A, IXL
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
                LD (@ActionObjectOffsetVectorState.Coefficient0), A
                ; Расчёт двух вкладов второго коэффициента с сохранением промежуточного байта в IXH.
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
                SUB IXH
                JP PO, @Action.BuildObjectOffsetCoefficients.StoreSecond        ; переход, если вычитание вкладов не переполнилось, записать второй коэффициент

                NEG
                JP PO, @Action.BuildObjectOffsetCoefficients.StoreSecond        ; переход, если отрицание не переполнилось, записать второй коэффициент

                DEC A
StoreSecond:    LD (@ActionObjectOffsetVectorState.Coefficient1), A
                ; Расчёт двух вкладов третьего коэффициента.
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
                ADD A, IXH
                JP PO, @Action.BuildObjectOffsetCoefficients.StoreThird         ; переход, если сложение вкладов не переполнилось, записать третий коэффициент

                NEG
                JP PO, @Action.BuildObjectOffsetCoefficients.StoreThird         ; переход, если отрицание не переполнилось, записать третий коэффициент

                DEC A
StoreThird:     LD (@ActionObjectOffsetVectorState.Coefficient2), A
                RET

                endmodule
                endmodule
