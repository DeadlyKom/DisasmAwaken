                module Map
                module RasterizeArcEdges
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [входы, байтовые счётчики, общий кадр и границы моделей](../../Docs/ArcKernel.md)
; -----------------------------------------
; Рекуррентная инверсия одного либо двух краёв дуги с растровыми границами и закрытием байтов
; исходная запись 7, файловые смещения #22AB..#2513
; In:
;   Entry начинает с левого края, BothEdges с двух краёв, RightEdge с правого края
;   HL адресует правый байт, DE - E младший адрес левого байта в той же группе строки, BC - B левая и C правая одноразрядные маски
;   HL' содержит начальный error, DE' счётчик Y, BC' счётчик X, обычный сброс задаёт HL'=0, D'=0, B'=FF
;   для однокраевого начала A' задаёт байтовый предел C' перехода к двум краям, входной F' не управляет алгоритмом
;   RasterDown=0 выбирает PreviousRasterRow, ненулевой байт выбирает NextRasterRow, границы и допустимые адреса заданы вызывающим
;   SP указывает на FArcReturnFrame с сохранённым AF перед настоящим адресом возврата, банк KARTA выбран
;   четыре изменяемых JR закрывающих масок подготовлены согласованным кодом 38 либо 30, bitmap и рабочий стек доступны
; Out:
;   граничные пиксели инвертируются через XOR одноразрядными масками, переходы между строками проверяют UpperRow и LowerRow
;   шаг Y прибавляет к error старое DE', увеличивает только E' и прибавляет новое DE', шаг X аналогичен для BC' и C'
;   знак проверяется по биту 15 оборачиваемого error, вертикальный и горизонтальный режимы выбирают порядок шагов X/Y
;   однокраевой проход сравнивает увеличенный C' с A' между двумя сложениями, при равенстве продолжает общий двухкраевой шаг
;   переносы масок меняют младшие байты адресов, однокраевой выход срабатывает после пересечения фиксированного крайнего байта
;   встреча байтов двух краёв завершает вертикальный режим сразу, горизонтальный через CloseLowTail либо CloseHighTail
;   при оборачивании C' в горизонтальном однокраевом режиме выполнение возвращается с активным набором рекурсии после EXX
;   при обычном сбросе такой выход даёт основной BC=FF00, D=0, альтернативные пары содержат растровые адреса и маски
;   на всех выходах AF восстанавливается из кадра, SP равен адресу кадра плюс FArcReturnFrame, HL, DE, BC и альтернативные пары рабочие
;   A' сохраняет байтовый предел, F' рабочий на однокраевых путях, на самостоятельном BothEdges весь AF' сохраняется
;   IX, IY, I и IFF сами инструкции сохраняют, RasterStack обновляется при начале непустого прохода
; Corrupt:
;   HL, DE, BC, AF из кадра, HL', DE', BC', AF' только F' на однокраевых путях, bitmap и RasterStack
; Note:
;   начальные совпадающие с выбранной границей строки пропускаются, после начала верхняя строка включена, нижняя исключена
;   B'=FF и D'=0 не увеличиваются вместе с младшими счётчиками, C'=0 означает BC'=FF00, это не знаковый ноль
;   CloseLowTail и CloseHighTail принимают растровый набор как основной и восстанавливают SP из RasterStack
;   CloseBothTails начинает с EXX, его вход передаёт растровый набор альтернативными парами, порядок двух записей существенен
;   RestoreFrame является общим нелокальным выходом, он читает кадр по RasterStack независимо от текущего SP
;   [Рекурсия](../../Docs/ArcRecurrence.md), [закрывающие маски](../../Docs/ArcClosing.md) и [подготовки](../../Docs/ArcPreparation.md) имеют отдельные модели
;   разбор описывает фактический алгоритм, модели покрывают указанные профили, весь диспетчер DFC3 и все игровые входы не объявляются проверенными
; -----------------------------------------
                ; выбор верхней либо нижней границы начальной строки для левого края
Entry:          LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.CheckLeftLower                    ; переход, если RasterDown ненулевой, проверить нижнюю начальную строку

                PUSH HL
                LD A, L
                AND #E0
                LD L, A
                LD A, E
                LD DE, (@MapState.UpperRow)
                OR A
                SBC HL, DE
                LD E, A
                POP HL
                JR NZ, @Map.RasterizeArcEdges.SaveLeftFrame                     ; переход, если строка не равна верхней границе, начать левый проход

                JR @Map.RasterizeArcEdges.ReturnLeftAF

                ; проверка адреса начальной строки по исключённой нижней границе
CheckLeftLower: PUSH HL
                LD A, L
                AND #E0
                LD L, A
                LD A, E
                LD DE, (@MapState.LowerRow)
                OR A
                SBC HL, DE
                LD E, A
                POP HL
                JR NZ, @Map.RasterizeArcEdges.SaveLeftFrame                     ; переход, если строка не равна исключённой нижней границе, начать левый проход

ReturnLeftAF:   POP AF
                RET

                ; сохранение SP внешнего кадра перед рисованием левого края
SaveLeftFrame:  LD (@MapState.RasterStack), SP
                ; инверсия пикселя левого края в вертикальном режиме
LeftVertical:   LD D, L
                LD L, E
                LD A, B
                XOR (HL)
                LD (HL), A
                LD L, D
                LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.StepLeftDown                      ; переход, если RasterDown ненулевой, перейти на строку ниже

                CALL @Map.PreviousRasterRow.Entry
                JR @Map.RasterizeArcEdges.LeftYStep

StepLeftDown:   CALL @Map.NextRasterRow.Entry
                ; расчёт error+DE'+новое DE' после увеличения только E'
LeftYStep:      EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JR NZ, @Map.RasterizeArcEdges.LeftVertical                      ; переход, если error отрицателен после шага Y, продолжить левую вертикаль

                RRC B
                JR C, @Map.RasterizeArcEdges.CrossLeftLimit                     ; переход, если левая маска перешла границу байта, увеличить E

                ; расчёт первого слагаемого шага X и увеличение только C' перед проверкой предела A'
LeftXStep:      EXX
                ADD HL, BC
                INC C
                EX AF, AF'
                CP C
                JR Z, @Map.RasterizeArcEdges.JoinBothVert                       ; переход, если C' равен пределу A', подключить второй край после первого слагаемого X

                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
                JR NZ, @Map.RasterizeArcEdges.LeftVertical                      ; переход, если error отрицателен после шага X, продолжить левую вертикаль

                JR @Map.RasterizeArcEdges.LeftHorizontal

                ; перенос левого маски в соседний байт и проверка пересечения фиксированной колонки
CrossLeftLimit: INC E
                LD A, L
                SUB E
                JR C, @Map.RasterizeArcEdges.RestoreLeftAF                      ; переход, если левый байт стал больше фиксированного правого, завершить проход

                JR @Map.RasterizeArcEdges.LeftXStep

                ; восстановление рабочего AF перед общим завершением вертикального шага X двух краёв
JoinBothVert:   EX AF, AF'
                JP @Map.RasterizeArcEdges.CompleteXStep

                ; восстановление рабочего AF перед общим завершением горизонтального шага X двух краёв
JoinBothHorz:   EX AF, AF'
                JP @Map.RasterizeArcEdges.EndHorzXStep

                ; возврат к внешнему кадру, при нулевом C' общий набор может оставаться обменённым через EXX
RestoreLeftAF:  LD SP, (@MapState.RasterStack)
                POP AF
                RET

                ; перенос маски левого края в горизонтальном режиме и проверка выхода за фиксированный байт
LeftLimitHorz:  INC E
                LD A, L
                SUB E
                JR C, @Map.RasterizeArcEdges.RestoreLeftAF                      ; переход, если левый байт стал больше фиксированного правого, завершить проход

                JR @Map.RasterizeArcEdges.LeftHorzXStep

                ; инверсия следующего пикселя левого края в той же строке
LeftHorizontal: LD D, L
                LD L, E
                LD A, B
                XOR (HL)
                LD (HL), A
                LD L, D
                RRC B
                JR C, @Map.RasterizeArcEdges.LeftLimitHorz                      ; переход, если левая маска перешла границу байта, проверить фиксированную колонку

                ; расчёт приращения X, нулевой C' завершает проход ещё до восстановления основного набора
LeftHorzXStep:  EXX
                ADD HL, BC
                INC C
                JR Z, @Map.RasterizeArcEdges.RestoreLeftAF                      ; переход, если C' обернулся в ноль, завершить с обменёнными общими парами

                EX AF, AF'
                CP C
                JR Z, @Map.RasterizeArcEdges.JoinBothHorz                       ; переход, если C' равен пределу A', подключить второй край в горизонтальном режиме

                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Map.RasterizeArcEdges.LeftHorizontal                     ; переход, если error неотрицателен, продолжить левое сближение в той же строке

                EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                EXX
                LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.MoveLeftDown                      ; переход, если RasterDown ненулевой, выполнить следующий шаг строки вниз

                CALL @Map.PreviousRasterRow.Entry
                JR @Map.RasterizeArcEdges.LeftHorizontal

MoveLeftDown:   CALL @Map.NextRasterRow.Entry
                JR @Map.RasterizeArcEdges.LeftHorizontal

                ; проверка порядка младших байтов левого E и правого L краёв перед двухкраевым проходом
BothEdges:      LD A, E
                SUB L
                JR NC, @Map.RasterizeArcEdges.ReturnSavedAF                     ; переход, если левый байт не раньше правого, вернуть сохранённый AF без рисования

                ; выбор границы начальной строки по направлению растрового прохода
                LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.CheckLower                        ; переход, если RasterDown ненулевой, проверить исключённую нижнюю строку

                ; проверка верхней строки по адресу без колонки с временным сохранением правого края
                PUSH HL
                LD A, L
                AND #E0
                LD L, A
                LD A, E
                LD DE, (@MapState.UpperRow)
                OR A
                SBC HL, DE
                LD E, A
                POP HL
                JR NZ, @Map.RasterizeArcEdges.SaveBothFrame                     ; переход, если начальная строка отличается от верхней границы, начать проход

                JR @Map.RasterizeArcEdges.ReturnSavedAF

                ; проверка нижней строки по адресу без колонки с сохранением младшего адреса левого края
CheckLower:     PUSH HL
                LD A, L
                AND #E0
                LD L, A
                LD A, E
                LD DE, (@MapState.LowerRow)
                OR A
                SBC HL, DE
                LD E, A
                POP HL
                JR NZ, @Map.RasterizeArcEdges.SaveBothFrame                     ; переход, если начальная строка отличается от исключённой нижней, начать проход

                ; восстановление AF внешнего входа, лежащего перед настоящим адресом возврата
ReturnSavedAF:  POP AF
                RET

                ; сохранение SP кадра для нелокальных выходов строковых помощников и закрывающих масок
SaveBothFrame:  LD (@MapState.RasterStack), SP
                ; инверсия пикселя правого края в вертикальном режиме рекурсии
BothVertical:   LD A, C
                XOR (HL)
                LD (HL), A
                ; выбор адреса левого края и инверсия его пикселя без потери правого адреса
                LD D, L
                LD L, E
                LD A, B
                XOR (HL)
                LD (HL), A
                LD L, D
                ; выбор следующей пиксельной строки по RasterDown
                LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.StepBothDown                      ; переход, если RasterDown ненулевой, двигать оба края вниз

                CALL @Map.PreviousRasterRow.Entry
                JR @Map.RasterizeArcEdges.AddVerticalStep

StepBothDown:   CALL @Map.NextRasterRow.Entry
                ; расчёт нового error как error+y+(y+1), увеличение y хранится в E'
AddVerticalStep:EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JP NZ, @Map.RasterizeArcEdges.BothVertical                      ; переход, если обновлённый 16-битный error отрицателен, оставить X и рисовать новую строку

                ; расчёт маски следующего левого пикселя, X увеличивается на один
                RRC B
                JR C, @Map.RasterizeArcEdges.CrossLeftByte                      ; переход, если левая маска прошла младший бит, увеличить адрес её байта

                ; расчёт маски следующего правого пикселя, X уменьшается на один
RotateRight:    RLC C
                JR C, @Map.RasterizeArcEdges.CrossRightByte                     ; переход, если правая маска прошла старший бит, уменьшить адрес её байта

                ; расчёт нового error как error+x+(x+1), увеличение x хранится в C'
BeginXStep:     EXX
                ADD HL, BC
                INC C
                ; завершение приращения error вторым слагаемым после увеличения x
CompleteXStep:  ADD HL, BC
                BIT 7, H
                EXX
                JP NZ, @Map.RasterizeArcEdges.BothVertical                      ; переход, если error отрицателен после шага X, продолжить вертикальный режим

                ; переход к сближению краёв в пределах текущей строки при неотрицательном error
                JP @Map.RasterizeArcEdges.BothHorizontal

                ; увеличение адреса левого байта после переноса одноразрядной маски
CrossLeftByte:  INC E
                LD A, L
                ; проверка встречи байтов после переноса левого края
                SUB E
                JP NZ, @Map.RasterizeArcEdges.RotateRight                       ; переход, если адреса байтов различаются, обработать правую маску

                ; восстановление внешнего кадра при встрече байтов в вертикальном режиме без закрывающей маски
                LD SP, (@MapState.RasterStack)
                POP AF
                RET

                ; уменьшение адреса правого байта и проверка встречи с левым
CrossRightByte: DEC L
                LD A, L
                SUB E
                JP NZ, @Map.RasterizeArcEdges.BeginXStep                        ; переход, если адреса байтов различаются, обновить ошибку шага X

                ; восстановление SP сохранённого внешнего кадра перед POP AF и настоящим RET
RestoreFrame:   LD SP, (@MapState.RasterStack)
                POP AF
                RET

                ; увеличение адреса левого байта в горизонтальном режиме и проверка встречи
CrossLeftHorz:  INC E
                LD A, L
                SUB E
                JP NZ, @Map.RasterizeArcEdges.RotateRightHorz                   ; переход, если байты ещё различаются, продолжить поворот правой маски

                ; закрытие младшего хвоста общего байта при встрече после левого переноса
                JR @Map.RasterizeArcEdges.CloseLowTail

                ; уменьшение адреса правого байта в горизонтальном режиме и проверка встречи
CrossRightHorz: DEC L
                LD A, L
                SUB E
                JP NZ, @Map.RasterizeArcEdges.BeginHorzXStep                    ; переход, если байты ещё различаются, продолжить приращение ошибки X

                ; закрытие старшего хвоста общего байта при встрече после правого переноса
                JR @Map.RasterizeArcEdges.CloseHighTail

                ; инверсия правого пикселя при сближении краёв в одной строке
BothHorizontal: LD A, C
                XOR (HL)
                LD (HL), A
                ; инверсия левого пикселя и восстановление правого младшего адреса
                LD D, L
                LD L, E
                LD A, B
                XOR (HL)
                LD (HL), A
                LD L, D
                ; расчёт следующей левой маски для уменьшения расстояния между краями
                RRC B
                JR C, @Map.RasterizeArcEdges.CrossLeftHorz                      ; переход, если левая маска перешла границу байта, проверить встречу и младший хвост

                ; расчёт следующей правой маски в горизонтальном режиме
RotateRightHorz:RLC C
                JR C, @Map.RasterizeArcEdges.CrossRightHorz                     ; переход, если правая маска перешла границу байта, проверить встречу и старший хвост

                ; расчёт приращения ошибки X с проверкой оборачивания счётчика C'
BeginHorzXStep: EXX
                ADD HL, BC
                INC C
                JR Z, @Map.RasterizeArcEdges.CloseBothTails                     ; переход, если C' обернулся в ноль, выполнить обе закрывающие маски

                ; завершение приращения ошибки X и проверка его 16-битного знака
EndHorzXStep:   ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Map.RasterizeArcEdges.BothHorizontal                     ; переход, если error неотрицателен, продолжить сближение в той же строке

                ; расчёт приращения ошибки Y перед переходом к следующей строке горизонтального режима
                EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                EXX
                ; выбор направления строкового шага после обновления ошибки Y
                LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.MoveHorzDown                      ; переход, если RasterDown ненулевой, перейти на строку ниже

                CALL @Map.PreviousRasterRow.Entry
                JR @Map.RasterizeArcEdges.BothHorizontal

MoveHorzDown:   CALL @Map.NextRasterRow.Entry
                JR @Map.RasterizeArcEdges.BothHorizontal

                ; выбор адреса левого байта, условие режима определяет закрытие младшего хвоста единиц или нулей
CloseLowTail:   LD L, E
                LD A, (HL)
                LD B, #00
                AND A
                JR Z, @Map.RasterizeArcEdges.ApplyInverseB                      ; переход, если исходный байт равен нулю, общая маска установит все восемь битов

                LD B, A
                LD A, #FF
                ; поиск младшего граничного бита, JR C принимает единицу, JR NC принимает ноль
ScanLowTail:    SRL B
                JR C, @Map.RasterizeArcEdges.ApplyLowMask                       ; переход, если крайний проверяемый бит равен 1 для JR C или 0 для JR NC, применить подготовленную маску

                ADD A, A
                JR @Map.RasterizeArcEdges.ScanLowTail

                ; для ненулевого v, JR C даёт v OR(v-1), JR NC даёт v AND(v+1), все значения байтовые
ApplyLowMask:   CPL
                XOR (HL)
                LD (HL), A
                JR @Map.RasterizeArcEdges.CloseAndExit

                ; проверка байта правого адреса перед закрытием его старшего хвоста согласно режиму
CloseHighTail:  LD A, (HL)
                LD B, #00
                AND A
                JR Z, @Map.RasterizeArcEdges.ApplyInverseB                      ; переход, если исходный байт равен нулю, общая маска установит все восемь битов

                DEC B
                ; поиск старшего граничного бита, каждый пропущенный бит сужает B согласно условию JR
ScanHighTail:   ADD A, A
                JR C, @Map.RasterizeArcEdges.ApplyInverseB                      ; переход, если крайний проверяемый бит равен 1 для JR C или 0 для JR NC, применить подготовленную маску

                SRL B
                JR @Map.RasterizeArcEdges.ScanHighTail

                ; обновление выбранного байта маской NOT B, JR C устанавливает старшие нули, JR NC очищает старшие единицы
ApplyInverseB:  LD A, B
                CPL
                XOR (HL)
                LD (HL), A
                ; завершение через сохранённый RasterStack, текущий вложенный стек не используется
CloseAndExit:   JP @Map.RasterizeArcEdges.RestoreFrame

                ; возврат растровых адресов в основной набор после рекуррентного шага с EXX
CloseBothTails: EXX
                LD A, (HL)
                AND A
                JR Z, @Map.RasterizeArcEdges.WriteRightLow                      ; переход, если правый байт равен нулю, дополнение нулевого A даст восемь единиц

                LD B, A
                LD A, #FF
                ; поиск младшего граничного бита правого байта для режима JR C или JR NC
ScanRightLow:   SRL B
                JR C, @Map.RasterizeArcEdges.WriteRightLow                      ; переход, если крайний проверяемый бит равен 1 для JR C или 0 для JR NC, записать младшую маску

                ADD A, A
                JR @Map.RasterizeArcEdges.ScanRightLow

                ; обновление правого байта, затем чтение левого после этой записи, адреса могут совпадать
WriteRightLow:  CPL
                XOR (HL)
                LD (HL), A
                LD L, E
                LD A, (HL)
                LD B, #00
                AND A
                JR Z, @Map.RasterizeArcEdges.WriteLeftHigh                      ; переход, если уже прочитанный левый байт равен нулю, установить все восемь битов

                DEC B
                ; поиск старшего граничного бита текущего левого байта согласно режиму JR
ScanLeftHigh:   ADD A, A
                JR C, @Map.RasterizeArcEdges.WriteLeftHigh                      ; переход, если крайний проверяемый бит равен 1 для JR C или 0 для JR NC, применить старшую маску

                SRL B
                JR @Map.RasterizeArcEdges.ScanLeftHigh

                ; закрытие старшего хвоста, JR C устанавливает нули, JR NC очищает единицы, нулевой вход отдельно даёт FF
WriteLeftHigh:  LD A, B
                CPL
                XOR (HL)
                LD (HL), A
                JR @Map.RasterizeArcEdges.CloseAndExit

                ; выбор верхней либо нижней границы начальной строки для правого края
RightEdge:      LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.CheckRightLower                   ; переход, если RasterDown ненулевой, проверить нижнюю начальную строку

                PUSH HL
                LD A, L
                AND #E0
                LD L, A
                LD A, E
                LD DE, (@MapState.UpperRow)
                OR A
                SBC HL, DE
                LD E, A
                POP HL
                JR NZ, @Map.RasterizeArcEdges.SaveRightFrame                    ; переход, если строка не равна верхней границе, начать правый проход

                JR @Map.RasterizeArcEdges.ReturnRightAF

                ; проверка адреса начальной строки по исключённой нижней границе
CheckRightLower:PUSH HL
                LD A, L
                AND #E0
                LD L, A
                LD A, E
                LD DE, (@MapState.LowerRow)
                OR A
                SBC HL, DE
                LD E, A
                POP HL
                JR NZ, @Map.RasterizeArcEdges.SaveRightFrame                    ; переход, если строка не равна исключённой нижней, начать правый проход

ReturnRightAF:  POP AF
                RET

                ; сохранение SP внешнего кадра перед рисованием правого края
SaveRightFrame: LD (@MapState.RasterStack), SP
                ; инверсия пикселя правого края в вертикальном режиме
RightVertical:  LD A, C
                XOR (HL)
                LD (HL), A
                LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.StepRightDown                     ; переход, если RasterDown ненулевой, двигать правый край вниз

                CALL @Map.PreviousRasterRow.Entry
                JR @Map.RasterizeArcEdges.RightYStep

StepRightDown:  CALL @Map.NextRasterRow.Entry
                ; расчёт error+DE'+новое DE' после увеличения только E'
RightYStep:     EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JR NZ, @Map.RasterizeArcEdges.RightVertical                     ; переход, если error отрицателен после шага Y, продолжить правую вертикаль

                RLC C
                JR C, @Map.RasterizeArcEdges.CrossRightLimit                    ; переход, если правая маска перешла границу байта, уменьшить L

                ; расчёт первого слагаемого шага X и увеличение только C' перед проверкой предела A'
RightXStep:     EXX
                ADD HL, BC
                INC C
                EX AF, AF'
                CP C
                JR Z, @Map.RasterizeArcEdges.JoinRightVert                      ; переход, если C' равен пределу A', подключить левый край после первого слагаемого X

                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
                JR NZ, @Map.RasterizeArcEdges.RightVertical                     ; переход, если error отрицателен после шага X, продолжить правую вертикаль

                JR @Map.RasterizeArcEdges.RightHorizontal

                ; перенос правого маски в соседний байт и проверка пересечения фиксированной колонки
CrossRightLimit:DEC L
                LD A, L
                SUB E
                INC A
                JR Z, @Map.RasterizeArcEdges.RestoreRightAF                     ; переход, если правый байт стал на единицу меньше фиксированного левого, завершить проход

                JR @Map.RasterizeArcEdges.RightXStep

                ; восстановление рабочего AF перед общим завершением вертикального шага X двух краёв
JoinRightVert:  EX AF, AF'
                JP @Map.RasterizeArcEdges.CompleteXStep

                ; восстановление рабочего AF перед общим завершением горизонтального шага X двух краёв
JoinRightHorz:  EX AF, AF'
                JP @Map.RasterizeArcEdges.EndHorzXStep

                ; возврат к внешнему кадру, при нулевом C' общий набор может оставаться обменённым через EXX
RestoreRightAF: LD SP, (@MapState.RasterStack)
                POP AF
                RET

                ; перенос маски правого края в горизонтальном режиме и проверка выхода за фиксированный байт
RightLimitHorz: DEC L
                LD A, L
                SUB E
                INC A
                JR Z, @Map.RasterizeArcEdges.RestoreRightAF                     ; переход, если правый байт стал на единицу меньше фиксированного левого, завершить проход

                JR @Map.RasterizeArcEdges.RightHorzXStep

                ; инверсия следующего пикселя правого края в той же строке
RightHorizontal:LD A, C
                XOR (HL)
                LD (HL), A
                RLC C
                JR C, @Map.RasterizeArcEdges.RightLimitHorz                     ; переход, если правая маска перешла границу байта, проверить фиксированную колонку

                ; расчёт приращения X, нулевой C' завершает проход ещё до восстановления основного набора
RightHorzXStep: EXX
                ADD HL, BC
                INC C
                JR Z, @Map.RasterizeArcEdges.RestoreRightAF                     ; переход, если C' обернулся в ноль, завершить с обменёнными общими парами

                EX AF, AF'
                CP C
                JR Z, @Map.RasterizeArcEdges.JoinRightHorz                      ; переход, если C' равен пределу A', подключить левый край в горизонтальном режиме

                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Map.RasterizeArcEdges.RightHorizontal                    ; переход, если error неотрицателен, продолжить правое сближение в той же строке

                EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                EXX
                LD A, (@MapState.RasterDown)
                AND A
                JR NZ, @Map.RasterizeArcEdges.MoveRightDown                     ; переход, если RasterDown ненулевой, выполнить следующий шаг строки вниз

                CALL @Map.PreviousRasterRow.Entry
                JR @Map.RasterizeArcEdges.RightHorizontal

MoveRightDown:  CALL @Map.NextRasterRow.Entry
                JR @Map.RasterizeArcEdges.RightHorizontal

                endmodule
                endmodule
