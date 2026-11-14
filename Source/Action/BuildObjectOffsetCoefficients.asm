                module Action
                module BuildObjectOffsetCoefficients
                ; Документация [алгоритм и проверка](../../Docs/ActionObjectOffsetCoefficients.md)
                ; -----------------------------------------
                ; Подготовка коэффициентов смещения по трём фазовым парам
                ; исходная запись 17, адреса B044..B0E8
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают
                ;   Offset0..2 содержат байтовые индексы x, y, z, страницы фаз 9900 и табличных квадратов 9800 читаемы
                ;   три операнда Coefficient0..2 доступны для записи, код ACTION банка 0 не перекрыт ими или рамкой возврата
                ;   CPU-стек содержит внешний возврат, IRQ и повторный вход не вмешиваются в общие операнды
                ; Out:
                ;   HL - H=98, L=(s(P(u,b))-s(d)+d) AND FF
                ;   DE - D=d, E=T[(s(P(u,b))-s(d)) AND FF], BC=256*b+c
                ;   AF - A равен третьему коэффициенту, F от заключительного ADD, NEG либо DEC по условиям знаковой коррекции
                ;   HL', DE', BC', AF' сохраняются
                ;   IX - IXH=P(v,c), IXL=u, IYH сохраняется, IYL=v
                ;   Coefficient0..2 содержат три байта по формулам ActionObjectOffsetCoefficients.md, иные байты RAM не записываются
                ;   SP=входной SP+2, I, IM, IFF и paging сохраняются, порты не используются
                ;   R учитывает 135 M1 плюс две условные коррекции, его старший бит сохраняется
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, IYL, R, три байта Coefficient0..2
                ; Note:
                ;   b=W[x], c=W[(x+64) AND FF], u=W[y], v=W[(y+64) AND FF], d=W[z], e=W[(z+64) AND FF]
                ;   W обозначает страницу 9900, T страницу 9800, s(a)=floor(s8(a)/2), P(a,b)=(T[(s(a)-s(b)+b) AND FF]-T[(s(a)-s(b)) AND FF]) AND FF
                ;   переполнение второй и третьей разности исправляется исходным NEG, его переполнение для 80 исправляется DEC до 7F
                ;   каждая выполненная коррекция NEG добавляет три M1, её дополнительный DEC добавляет ещё одну M1
                ;   собственных записей CPU-стека нет, RET снимает внешний адрес, CALL вызывающего относится к его рамке
                ;   8192 самостоятельных сценария и 73728 проходов обёртки проверяют точные регистры, R и исходные записи, это не полный перебор всех таблиц
                ;   IRQ, точные T и нативный запуск этой проверкой не подтверждены
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
