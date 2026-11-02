                module Controls
                module BuildParameterTables
                ; Документация [алгоритм и проверка](../../Docs/ControlsParameterTables.md)
                ; -----------------------------------------
                ; Формирование пятнадцати параметров и девяти строковых значений по зерну и исходным таблицам
                ; исходная запись 23, банк 1, смещения #0332..#03BB
                ; In:
                ;   HL, DE, BC и AF основных аргументов не задают, первое зерно читается из SeedFirst, второе из SeedSecond, управляющий байт из StepControl
                ;   входные HL' и DE' становятся основными выходными HL и DE из-за конечного EXX, остальные альтернативные входы не задают числовых параметров
                ;   банк 1 выбран, общее ядро ACTION перенесено, используются исходные таблицы параметров, строк и пятнадцать FParameterCoefficient
                ;   физический FWordRandomState, Parameters, CoordRows и операнд SeedIndex по 688B доступны для записи
                ;   на CPU-стеке внешний возврат, ещё восемь байтов нужны настоящей вложенной цепочке, IRQ не вмешиваются
                ; Out:
                ;   HL=входной HL', DE=входной DE', BC=0000 OR C, где C является средним четырёхбитным индексом BuildSeededIndices
                ;   Parameters содержит 15 вычисленных байтов, CoordRows содержит девять записей через RowStride=6, промежутки не меняются
                ;   A равен последнему строковому шаблону плюс C по модулю байта, F=28 OR (F этого ADD AND C4)
                ;   HL'=7BCD, DE'=RowTemplates+16*G+9, BC'=0006, A' равен последнему Parameters[14], F' от последнего сложения с байтом шаблона параметра
                ;   IX=9BB3, IY, I, IM и IFF сохраняются, SP=входной SP+2
                ;   SeedIndex содержит индекс свёртки зерна 0..6, физическое состояние генератора соответствует всем K шагам
                ;   R учитывает настоящие вызовы и длины исходных циклов, точный счёт каждого пути проверен независимой моделью
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, Parameters, девять CoordRows, SeedIndex, состояние генератора, восемь байтов CPU-стека, R
                ; Note:
                ;   G равен старшему индексу BuildSeededIndices, но при нулевом индексе свёртки заменяется DefaultGroup=3
                ;   в исходной таблице код наклона 01 означает ноль, 02 означает плюс C, FE означает минус C, число SRA задаётся степенью двойки ShiftMask
                ;   шаблон параметров G=4 читает байты начала самой таблицы коэффициентов со смещением один, перекрытие сохраняется без копирования
                ;   688B является операндом LD A, n по 688A общего ядра ACTION, это настоящая самомодификация
                ;   последний EXX не компенсируется перед RET, описанный основной и альтернативный наборы нельзя менять местами
                ;   точные игровые имена пятнадцати полей и девяти строковых значений пока не установлены, числовой алгоритм разобран на исходных таблицах
                ; -----------------------------------------
                ; загрузка двух слов зерна и числа шагов из существующего контекста
Entry:          LD HL, (@ControlsParameterTablesState.SeedFirst)
                LD DE, (@ControlsParameterTablesState.SeedSecond)
                LD A, (@ControlsParameterTablesState.StepControl)
                ; формирование числовых индексов настоящей цепочкой классификатора и генератора
                CALL @Controls.BuildSeededIndices.Entry
                ; обновление операнда LD A, n по 688A общего ядра ACTION индексом свёртки зерна
                LD (@ControlsParameterTablesState.SeedIndex), A
                ; проверка нулевого индекса свёртки перед выбором группы шаблонов
                OR A
                JR NZ, @Controls.BuildParameterTables.SelectTemplates           ; переход, если индекс свёртки ненулевой, использовать вычисленную группу H

                ; выбор DefaultGroup для нулевого индекса свёртки
                LD H, @ControlsParameterTablesConst.DefaultGroup
                ; вычисление смещения группы как 16*H, диапазон H=0..4 исключает циклическое переполнение
SelectTemplates:LD A, H
                RLCA
                RLCA
                RLCA
                RLCA
                LD E, A
                LD D, #00
                ; вычисление среднего индекса C=0..15 из исходного L=1..16
                LD C, L
                DEC C
                ; сохранение группового смещения для последующего строкового шаблона
                PUSH DE
                ; вычисление указателя выбранного шаблона параметров без дублирования перекрытых байтов
                LD HL, @ControlsParameterTablesConst.ValueTemplates
                ADD HL, DE
                EX DE, HL
                ; сохранение среднего индекса C для последующего перехода в альтернативный BC
                PUSH BC
                ; выбор первого кода наклона физической трёхбайтовой записи
                LD HL, @ControlsParameterCoefficients.Field00.SlopeCode
                ; подготовка выхода на 15 последовательных байтов Parameters
                LD IX, @ControlsParameterTablesState.Parameters
                LD A, @ControlsParameterTablesConst.RecordCount
                ; сохранение счётчика полей в альтернативном AF на время вычисления значения
BuildField:     EX AF, AF'
                ; проверка знака кода наклона, исходные значения 01, 02 и FE задают ноль, плюс C и минус C
                LD A, (HL)
                AND A
                JP P, @Controls.BuildParameterTables.ScalePositive              ; переход, если код наклона неотрицательный, обработать 01 либо 02

                ; вычисление числа вычитаний как модуль отрицательного кода минус один
                NEG
                DEC A
                JR Z, @Controls.BuildParameterTables.ShiftField                 ; переход, если число вычитаний нулевое, продолжить с нулевой величиной

                ; подготовка исходной отрицательной суммы, для FE выполняется одно вычитание C
                LD B, A
                XOR A
SubtractSteps:  SUB C
                DJNZ @Controls.BuildParameterTables.SubtractSteps

                JR @Controls.BuildParameterTables.ShiftField

                ; вычисление числа сложений как положительный код минус один
ScalePositive:  DEC A
                JR Z, @Controls.BuildParameterTables.ShiftField                 ; переход, если код наклона равен 01, продолжить с нулевой величиной

                ; подготовка исходной положительной суммы, для 02 выполняется одно сложение C
                LD B, A
                XOR A
AddSteps:       ADD A, C
                DJNZ @Controls.BuildParameterTables.AddSteps

                ; чтение ShiftMask, позиция единственной единицы задаёт число арифметических сдвигов
ShiftField:     INC HL
                LD B, (HL)
                ; поиск младшей единицы ShiftMask с одновременным масштабированием знаковой суммы
ShiftUntilOne:  RR B
                JR C, @Controls.BuildParameterTables.AddBases                   ; переход, если младший проверяемый разряд ShiftMask установлен, масштабирование закончено

                SRA A
                JR @Controls.BuildParameterTables.ShiftUntilOne

                ; выбор поля Base текущего FParameterCoefficient и прибавление его к масштабированной величине
AddBases:       DEC HL
                DEC HL
                ADD A, (HL)
                ; прибавление байта выбранного группового шаблона к вычисленному полю
                EX DE, HL
                ADD A, (HL)
                EX DE, HL
                ; обновление очередного физического байта Parameters
                LD (IX+#00), A
                ; переход к следующему шаблонному байту, выходному байту и коду наклона, физический шаг правила равен трём
                INC DE
                INC IX
                INC HL
                INC HL
                INC HL
                INC HL
                ; восстановление счётчика полей и сохранение последнего значения с его F в альтернативном AF
                EX AF, AF'
                ; проверка числа оставшихся полей после записи очередного результата
                DEC A
                JP NZ, @Controls.BuildParameterTables.BuildField                ; переход, если обработаны ещё не все RecordCount полей

                ; восстановление среднего индекса в альтернативный C, затем выбор ранее сохранённой группы строк
                EXX
                POP BC
                EXX
                POP DE
                ; вычисление указателя строкового шаблона RowTemplates+16*G
                LD HL, @ControlsParameterTablesConst.RowTemplates
                ADD HL, DE
                EX DE, HL
                ; подготовка девяти записей CoordRows с физическим шагом RowStride
                LD HL, @ControlsParameterTablesState.CoordRows
                LD BC, @ControlsParameterTablesConst.RowStride
                ; обновление первой строки без прибавления среднего индекса
                LD A, (DE)
                LD (HL), A
                ADD HL, BC
                INC DE
                ; переход в альтернативный набор для счётчика восьми строк, этот EXX перед RET не компенсируется
                EXX
                LD B, @ControlsParameterTablesConst.ExtraRows
                ; чтение следующего шаблонного байта через основной указатель и прибавление сохранённого среднего индекса
WriteRows:      EXX
                LD A, (DE)
                EXX
                ADD A, C
                EXX
                ; обновление очередной строки, ADD HL, BC оставляет S, Z, PV от байтового сложения, но заменяет H, N, C и биты 5, 3
                LD (HL), A
                ADD HL, BC
                INC DE
                EXX
                DJNZ @Controls.BuildParameterTables.WriteRows

                RET

                endmodule
                endmodule
