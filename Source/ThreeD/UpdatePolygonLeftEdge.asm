                module ThreeD
                module UpdatePolygonLeftEdge
                ; Документация [алгоритм и проверка](../../Docs/ThreeDOverlayMirror.md)
                ; Документация [граница обновления ребра](../../Docs/ActionPolygonLeftEdge.md)
                ; -----------------------------------------
                ; Поиск восходящего левого ребра, вычисление целого шага и ошибки, выбор продолжения заливки
                ; исходная запись 19, банк 0, смещения #1272..#13A7
                ; In:
                ;   HL содержит H страницы масок, входной L не используется
                ;   DE содержит D текущей строки, входной E не используется, BC содержит сохраняемый линейный адрес
                ;   AF входных аргументов не задаёт, LeftCursor указывает нечётный байт First исходной вершины в странице 90
                ;   LastIndex содержит последний нечётный индекс кольца из 3..60 вершин, назад достижима вершина с First строго больше D
                ;   Second от 0 до 255, First от 0 до 95, высота выбранного ребра от 1 до 95
                ;   RightEndRow содержит текущую строку готовности правой цепочки, от 0 до 95
                ;   HL' содержит сохраняемый H' и заменяемую ошибку L', DE' сохраняется, BC' заменяется шагом, AF', IX и IY сохраняются
                ;   SP=FFE0, под ним доступны два байта существующего временного стека, IRQ не вмешиваются, 3DPART банка 0 доступен для записи
                ; Out:
                ;   HL сохраняет H, L становится входным RightEndRow
                ;   DE сохраняет D, E равен первоначальной Second при abs(dx)<Height, иначе E=(abs(dx) DIV Height) XOR #FF
                ;   BC сохраняется
                ;   AF содержит A=входной D и F от CP D,RightEndRow, условие готовности правой цепочки уже проверено
                ;   HL' сохраняет H', L'=Height DIV 2
                ;   DE' сохраняется, BC'=(#2000+32*s) AND #FFFF, s=ceil(dx/Height) для ненулевого dx, при dx=0 s=1 с дробной компенсацией
                ;   AF', IX и IY сохраняются
                ;   LeftCursor указывает найденный конец, LeftEndRow равен его First, Height равен разности First конца и входного D
                ;   dx равен Second найденного конца минус Second первоначальной вершины, пропущенные вершины начальную Second не заменяют
                ;   Subtract при dx<0 равен abs(dx) MOD Height, при неотрицательном точном длинном наклоне равен нулю, иначе Height-(dx MOD Height)
                ;   если D меньше RightEndRow, управление передано SelectPolygonRowLimit.Entry, RowLimit и RowBranch ещё не записаны
                ;   иначе RowLimit=RightEndRow, RowBranch=#3B и выполнен JP D229 для подготовки правого ребра
                ;   SP восстановлен до FFE0, два байта под ним содержат входные D и H, внешнего RET нет, I, IM, IFF и paging сохранены, R меняется
                ; Corrupt:
                ;   L, E, AF, L', BC', R, LeftCursor, Height, Subtract, LeftEndRow, два байта под SP и при необходимости RowLimit/RowBranch
                ; Note:
                ;   дисковая копия слота 19 побайтово совпадает с ACTION по исходным смещениям 6000..801F
                ;   перенос доказательств требует тех же внешней RAM, банка 0, состояния входа и договоров общих процедур вне файла
                ;   нативная загрузка отдельного 3DPART не выполнялась, CF08 сохраняет отдельную неоднозначность исполнения
                ;   поиск пропускает равные и меньшие строки и оборачивает обратное кольцо, бесконечный повреждённый список не исправляется
                ;   деление развёрнуто на восемь бит частного, каждый неудачный SUB восстанавливает остаток перед следующим разрядом
                ;   нулевой наклон использует шаг 2020 и Subtract=Height, это исходная комбинация плюс один с коррекцией минус один
                ;   в отличие от сходного кода предпросмотра основной AF не сохраняется через отдельный PUSH, финальные флаги относятся к проверке готовности правой цепочки
                ;   48545 сценариев левой цепочки из общей серии 97090 проверяют все высоты 1..95 и наклоны -255..255, регистры кроме R, RAM и кратность записей
                ;   проверены пропуски 0..58 вершин и оборачивание, все сочетания произвольных колец не исчерпаны
                ;   строковое ядро целиком, R/T, IRQ, сборка и нативное исполнение отдельно не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Контекст и обратный поиск
                ; Сохранение страницы масок и текущей строки в существующем временном стеке.
Entry:          LD L, D
                PUSH HL
                ; Чтение курсора левой цепочки и первоначальной Second, пропуск вершин её не перечитывает.
                LD HL, #0000
                DEC L
                LD E, (HL)
                INC L
                ; Поиск предыдущей First с оборачиванием при достижении начала списка.
PreviousRow:    DEC L
                JR Z, @ThreeD.WrapPolygonLeftEdge.Entry                         ; переход, если достигнута нулевая колонка страницы, перейти к последней First кольца

                DEC L
                ; Расчёт высоты кандидата относительно текущей строки.
ReadNextRow:    LD A, (HL)
                SUB D
                JR Z, @ThreeD.UpdatePolygonLeftEdge.PreviousRow                 ; переход, если высота равна нулю, пропустить горизонтальный участок

                JR C, @ThreeD.UpdatePolygonLeftEdge.PreviousRow                 ; переход, если First кандидата меньше текущей строки, продолжить поиск восходящего ребра

                ; Обновление конечной вершины, высоты ребра и его нижнего предела.
                LD (@ActionPolygonPreparationState.LeftCursor), HL
                LD D, A
                LD (@ActionPolygonLeftEdgeState.Height), A
                ; Расчёт начальной ошибки как половины высоты с округлением вниз и сохранение её в L'.
                RRA
                EXX
                LD L, A
                EXX
                LD A, (HL)
                LD (@ActionPolygonPreparationState.LeftEndRow), A
                ; Расчёт знакового горизонтального смещения относительно исходной Second.
                DEC L
                LD A, (HL)
                SUB E
                JP C, @ThreeD.UpdatePolygonLeftEdge.NegativeSlope               ; переход, если Second конца меньше исходной Second, обработать отрицательный наклон

                ; Проверка необходимости деления неотрицательного наклона на высоту.
                CP D
                JP C, @ThreeD.UpdatePolygonLeftEdge.ShortPositive               ; переход, если dx меньше высоты, использовать короткую положительную ветвь без деления

                ; -----------------------------------------
                ; Неотрицательное деление
                ; Подготовка модуля dx и нулевого остатка для восьми разрядов частного.
                LD E, A
                XOR A
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
                RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.PositiveBit0               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
PositiveBit0:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.PositiveBit1               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
PositiveBit1:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.PositiveBit2               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
PositiveBit2:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.PositiveBit3               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
PositiveBit3:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.PositiveBit4               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
PositiveBit4:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.PositiveBit5               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
PositiveBit5:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.PositiveBit6               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
PositiveBit6:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.PositiveBit7               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
PositiveBit7:   RL E
                ; Проверка точного деления после получения всех разрядов.
                AND A
                JR Z, @ThreeD.UpdatePolygonLeftEdge.ExactPositive               ; переход, если остаток равен нулю, вычитаемая ошибка равна нулю

                ; Расчёт дополнения остатка до высоты для вычитаемой ошибки и целого шага, округлённого вверх.
                SUB D
                NEG
                LD (@ActionPolygonLeftEdgeState.Subtract), A
                LD A, E
                NEG
                SRL A
                ; Упаковка целого шага в BC', один пиксель соответствует 32, строка добавляет 2000.
                EXX
                LD C, #00
                RR C
                RRA
                RR C
                RRA
                RR C
                ADD A, #20
                LD B, A
                EXX
                ; Восстановление страницы масок и текущей строки перед общей проверкой правой цепочки.
                POP HL
                LD D, L
                LD A, D
                JP @ThreeD.UpdatePolygonLeftEdge.CheckRightReady

                ; Точное неотрицательное деление, обновление нулевой ошибки и упаковка целого шага.
ExactPositive:  LD (@ActionPolygonLeftEdgeState.Subtract), A
                LD A, E
                CPL
                RRA
                EXX
                LD C, #00
                RR C
                SRA A
                RR C
                SRA A
                RR C
                ADD A, #20
                LD B, A
                EXX
                POP HL
                LD D, L
                LD A, D
                JP @ThreeD.UpdatePolygonLeftEdge.CheckRightReady

                ; -----------------------------------------
                ; Короткий неотрицательный наклон
                ; Расчёт вычитаемой ошибки Height-dx при фиксированном шаге плюс один пиксель.
ShortPositive:  SUB D
                NEG
                LD (@ActionPolygonLeftEdgeState.Subtract), A
                EXX
                LD C, #20
                LD B, C
                EXX
                POP HL
                LD D, L
                LD A, D
                JP @ThreeD.UpdatePolygonLeftEdge.CheckRightReady

                ; -----------------------------------------
                ; Отрицательное деление
                ; Расчёт модуля отрицательного dx и проверка короткой ветви.
NegativeSlope:  NEG
                CP D
                JR C, @ThreeD.UpdatePolygonLeftEdge.ShortNegative               ; переход, если abs(dx) меньше высоты, использовать нулевой целый горизонтальный шаг

                ; Подготовка модуля dx и нулевого остатка для отрицательного наклона.
                LD E, A
                XOR A
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
                RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.NegativeBit0               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
NegativeBit0:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.NegativeBit1               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
NegativeBit1:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.NegativeBit2               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
NegativeBit2:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.NegativeBit3               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
NegativeBit3:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.NegativeBit4               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
NegativeBit4:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.NegativeBit5               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
NegativeBit5:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.NegativeBit6               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
                ; Расчёт следующего разряда частного по удвоенному остатку и очередному разряду модуля dx.
NegativeBit6:   RL E
                RLA
                SUB D
                JR NC, @ThreeD.UpdatePolygonLeftEdge.NegativeBit7               ; переход, если пробное вычитание высоты не дало заёма, сохранить уменьшенный остаток

                ADD A, D
NegativeBit7:   RL E
                ; Обновление Subtract остатком отрицательного деления и упаковка целого шага.
                LD (@ActionPolygonLeftEdgeState.Subtract), A
                LD A, E
                INC A
                SCF
                RRA
                EXX
                LD C, #00
                RR C
                SRA A
                RR C
                SRA A
                RR C
                ADD A, #20
                LD B, A
                EXX
                POP HL
                LD D, L
                LD A, D
                ; -----------------------------------------
                ; Готовность правой цепочки
                ; Проверка текущей строки относительно уже подготовленного правого предела.
CheckRightReady:LD L, #00
                CP L
                JP C, @ThreeD.SelectPolygonRowLimit.Entry                       ; переход, если текущая строка меньше правого предела, выбрать ближайший из двух готовых рёбер

                ; Обновление предела и перехода для подготовки правой цепочки перед рисованием строки.
                LD A, L
                LD (@ActionPolygonPreparationState.RowLimit), A
                LD A, @ActionPolygonRowSelectionConst.RightOffset
                LD (@ActionPolygonPreparationState.RowBranch), A
                LD A, D
                JP @ThreeD.PolygonFillRows.CheckRow

                ; -----------------------------------------
                ; Короткий отрицательный наклон
                ; Обновление Subtract модулем dx, целый горизонтальный шаг равен нулю.
ShortNegative:  LD (@ActionPolygonLeftEdgeState.Subtract), A
                EXX
                LD C, #00
                LD B, #20
                EXX
                POP HL
                LD D, L
                LD A, D
                JP @ThreeD.UpdatePolygonLeftEdge.CheckRightReady

                ; -----------------------------------------
                endmodule
                endmodule
