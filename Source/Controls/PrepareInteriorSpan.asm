                module Controls
                module PrepareInteriorSpan
                ; Документация [алгоритм и проверка](../../Docs/ControlsInteriorRows.md)
                ; -----------------------------------------
                ; Подготовка полной внутренней маски и общие входы заливки строк
                ; исходная запись 22, банк 1, смещения #157B..#1608
                ; In:
                ;   HL задаёт L как младший байт текущего адреса, DE задаёт сохраняемый D
                ;   банк 1 выбран, на CPU-стеке внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   HL и D сохраняются, E=(входной L AND E0) OR 01, BC=00FF
                ;   AF содержит A=E и F логического OR, H, N и Carry сброшены, Z сброшен
                ;   HL', DE', BC', AF', IX и IY, I, IM и IFF сохраняются, SP=входной SP+2, R получает девять M1
                ; Corrupt:
                ;   E, BC, AF, R
                ; Note:
                ;   чтение Mode не влияет на выход начального входа, последующие AND и OR полностью заменяют F
                ;   FillRowsUp и FillRowsDown являются отдельными внутренними входами, их полный договор приведён в ControlsInteriorRows.md
                ;   внутренние входы принимают A=0..95, B как количество строк, IXL как рисунок и IXH как XOR-чередование
                ;   через FillRowsUp или FillRowsDown все 30 косвенных записей ограничены столбцами 1..30 растра 8000..8BFF, отдельно меняются D5B5..D5B6, D600..D601 и рамка SP-6..SP-1
                ;   внутренние входы сохраняют входные AF, DE и BC на CPU-стеке, требуют ещё шесть байтов, меняют HL и IXL
                ;   PrepareRows требует HL=3880 для движения вверх либо HL=308C вниз и уже записанный RowStep
                ;   FillRow является внутренней петлёй с сохранённой рамкой, RestoreFrame потребляет SavedBC, SavedAF, SavedDE и возврат
                ;   рамка внутренних FillRowsUp/FillRowsDown описана FInteriorRowsFrame, от текущего SP после трёх PUSH идут SavedBC, SavedAF, SavedDE и CallerReturn
                ; -----------------------------------------
                ; чтение Mode не определяет выход этого входа, F заменяется расчётом полной внутренней маски
Entry:          LD A, (@ControlsInteriorRowsState.Mode)
                AND A
                ; вычисление младшего адреса первого внутреннего столбца из адреса строки
                LD A, L
                AND #E0
                OR #01
                LD E, A
                ; подготовка полных масок C=FF и B=0 для отсутствующего правого ограничителя
                LD C, #FF
                LD B, #00
                RET

                ; -----------------------------------------
                ; Заливка строк вверх или вниз с изменением предела и кода перехода
                ; -----------------------------------------
                ; выбор RowStep=-32 для движения к предыдущей строке
FillRowsUp:     LD HL, #FFE0
                ; обновление существующего операнда RowStep
                LD (@ControlsInteriorRowsState.RowStep), HL
                ; подготовка двух байтов границы, LOW=80 для CP, HIGH=38 как код JR C
                LD HL, #3880
                JR @Controls.PrepareInteriorSpan.PrepareRows

                ; выбор RowStep=32 для движения к следующей строке
FillRowsDown:   LD HL, #0020
                ; обновление существующего операнда RowStep
                LD (@ControlsInteriorRowsState.RowStep), HL
                ; подготовка двух байтов границы, LOW=8C для CP, HIGH=30 как код JR NC
                LD HL, #308C
                ; обновление BoundaryLimit и самого кода BoundaryBranch одним словом
PrepareRows:    LD (@ControlsInteriorRowsState.BoundaryLimit), HL
                ; сохранение DE и номера строки с F от AND Mode в шестибайтовой рамке
                PUSH DE
                PUSH AF
                ; вычисление адреса правого крайнего столбца как 8000+32*A+31
                LD L, A
                LD H, #04
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD DE, #001F
                ADD HL, DE
                ; сохранение количества строк B и заменённого номером строки C
                PUSH BC
                ; проверка нулевого количества без изменения B, пара DEC и INC сохраняет исходный счётчик
                DEC B
                INC B
                JR Z, @Controls.PrepareInteriorSpan.RestoreFrame                ; переход, если количество строк B равно нулю, восстановить рамку в RestoreFrame

                LD DE, #0020
                ; сохранение правого столбца в C и выбор рисунка строки из IXL
FillRow:        LD C, L
                LD A, IXL
                ; заполнение столбцов 30..1 развёрнутой цепочкой, крайние столбцы 0 и 31 остаются нетронутыми
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                DEC L
                LD (HL), A
                ; вычисление правого крайнего столбца следующей строки с выбранным RowStep
                LD L, C
                ADD HL, DE
                ; вычисление рисунка следующей строки как IXL XOR IXH, выполняется и после последней записи
                LD A, IXL
                XOR IXH
                LD IXL, A
                ; проверка выхода за край растра, BoundaryLimit и BoundaryBranch изменены направлением
                LD A, H
                CP #00
                JR NC, @Controls.PrepareInteriorSpan.RestoreFrame               ; переход, если достигнут край, после настройки вверх условие H<80, вниз условие H>=8C

                ; проверка оставшегося количества строк после прохода, не пересёкшего край
                DJNZ @Controls.PrepareInteriorSpan.FillRow

                ; восстановление SavedBC, SavedAF и SavedDE, вычисленные HL и IXL сохраняются
RestoreFrame:   POP BC
                POP AF
                POP DE
                ; -----------------------------------------
                RET

                ; -----------------------------------------
                endmodule
                endmodule
