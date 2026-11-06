                module Action
                module ScheduleSpawn
                ; Документация [алгоритм и проверка](../../Docs/ActionSpawnSchedule.md)
                ; -----------------------------------------
                ; Планирование создания объекта, выбор класса, модели и начальных координат
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #1D95..#2010
                ; In:
                ;   Entry читает изменяемые операнды фазы, счётчика и порога, аргументы в регистрах ему не нужны
                ;   доступны список FActionRecord, рабочий вектор, таблицы класса и модели, банки 0, 1, 3 и 4 и незаблокированный 7FFD
                ; Out:
                ;   фаза определяет ранний возврат, переход на SpawnAlternate или попытку выделения записи
                ;   после выделения задаются класс, модель, координаты и начальные поля, управление передаётся в FinishSpawnRecord
                ;   ветка BuildPosition без числа целей пропускает изменение индекса, при ненулевом числе проверяет индекс и вызывает шаг к выбранной цели
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, рабочие записи, операнды кода, состояния потоков, 7FFD
                ; Note:
                ;   класс 3 недостижим через повторный порог #50, класс 8 дополнительно проверяет #9B82
                ;   BuildPosition зацикливается, если все три компоненты равны 0 или #8000, игровая достижимость не установлена
                ;   модели разделяют точки входа, полный выход регистров после диспетчера, IRQ и нативный игровой запуск не проверены
                ; -----------------------------------------
                ; Вращение фазового операнда и проверка прежнего младшего бита.
Entry:          LD A, #80
                RRCA
                LD (#7B59), A
                RET NC                                                          ; выход, если прежний младший бит фазы равен нулю

                NOP
                LD A, #00
                DEC A
                JP P, @Action.SpawnAlternate.SetCountdown                       ; переход, если уменьшенный счётчик неотрицателен

                CALL @Action.NextRandomWord0.Entry
                LD A, L
                CP #FD
                JP C, @Action.SpawnAlternate.CheckDistance                      ; переход, если младший байт потока 0 ниже порога

                CALL @Action.FindReusableRecord.Entry
                RET Z                                                           ; выход, если поиск свободной записи дошёл до маркера конца

                PUSH IY
                POP IX
                PUSH HL
                CALL @Action.NextRandomWord2.Entry
                CALL @Action.MaxFoldedVectorHigh.Entry
                LD A, L
                SRL A
                SRL A
                LD D, #99
                LD E, A
                LD A, (DE)
                LD D, A
                RRCA
                RRCA
                RRCA
                RRCA
                AND #07
                LD C, #00
                SUB H
                JR C, @Action.ScheduleSpawn.CheckClassZero                      ; переход, если старший байт потока 2 больше поправки

                XOR A
CheckClassZero: NEG
                CP #0A
                LD A, H
                NOP
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если скорректированное значение меньше 10, выбран класс 0

                CP #43
                LD C, #01
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если старший байт потока меньше #43, выбран класс 1

                CP #50
                LD C, #02
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если старший байт потока меньше #50, выбран класс 2

                CP #50
                LD C, #03
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если старший байт потока меньше #50, путь недостижим после предыдущей проверки

                CP #5A
                LD C, #04
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если старший байт потока меньше #5A, выбран класс 4

                CP #5E
                LD C, #05
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если старший байт потока меньше #5E, выбран класс 5

                CP #63
                LD C, #06
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если старший байт потока меньше #63, выбран класс 6

                CP #6B
                LD C, #07
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если старший байт потока меньше #6B, выбран класс 7

                CP #70
                LD C, #08
                JR C, @Action.ScheduleSpawn.CheckClassEight                     ; переход, если старший байт потока меньше #70, выбран класс 8

                POP DE
                RET

CheckClassEight:LD A, C
                CP #08
                JR NZ, @Action.ScheduleSpawn.SelectModel                        ; переход, если выбран класс, отличный от 8

                LD A, (#9B82)
                OR A
                JR Z, @Action.ScheduleSpawn.SelectModel                         ; переход, если #9B82 равен нулю и разрешает класс 8

                POP DE
                RET

                ; Запись класса и выбор одной из восьми пар по младшим трём битам R.
SelectModel:    LD (IX + @FActionRecord.ClassCode), C
                SLA C
                LD B, #00
                LD HL, #7AC6
                ADD HL, BC
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                LD A, R
                AND #07
                RLA
                ADD A, L
                LD L, A
                LD A, H
                ADC A, #00
                LD H, A
                LD A, (HL)
                LD (IX+#06), A
                INC HL
                LD L, (HL)
                LD (IX+#0F), L
                LD H, D
                POP DE
                LD L, A
                LD A, (IX + @FActionRecord.ClassCode)
                CP #06
                JR Z, @Action.ScheduleSpawn.CreateEffect                        ; переход, если класс равен 6

                CP #07
                JR Z, @Action.ScheduleSpawn.CreateEffect                        ; переход, если класс равен 7

                LD A, #80
                SUB H
                LD H, A
                LD A, #80
                SUB D
                SRL A
                ADD A, #19
                CP H
                JP C, @Action.ScheduleSpawn.TryNearby                           ; переход, если байтовый порог ((#80−D) / 2) + #19 меньше #80−H до замены H

                LD A, C
                CP #10
                JP Z, @Action.ScheduleSpawn.TryNearby                           ; переход, если удвоенный класс равен #10

                ; Чтение режима модели и подготовка случайных координат малого эффекта.
CreateEffect:   LD A, L
                CALL @Action.ReadObjectHeaderWord.Entry
                LD A, H
                PUSH AF
                CALL @Action.NextRandomWord4.Entry
                SRA H
                RR L
                LD (IX+#04), L
                LD (IX+#05), H
                PUSH HL
                CALL @Action.NextRandomWord1.Entry
                SRA H
                RR L
                LD (IX+#02), L
                LD (IX+#03), H
                PUSH HL
                CALL @Action.NextRandomWord5.Entry
                SRA H
                RR L
                LD (IX+#00), L
                LD (IX+#01), H
                POP DE
                POP BC
                POP AF
                EX AF, AF'
                LD A, #1A
                EXX
                LD HL, #EC00
                CALL @Action.DispatchBank3Callback.Entry
                LD A, #01
                LD (#6D39), A
                LD A, (#6D3D)
                CP #1A
                JR NC, @Action.ScheduleSpawn.AimWithEffect                      ; переход, если остаток кадров обхода не меньше 26

                LD A, #1A
                LD (#6D3D), A
AimWithEffect:  LD (IX + @FActionRecord.Unknown0A), #01
                CALL @Action.SelectWideTargetAndStep.Entry
                JP @Action.FinishSpawnRecord.Entry

                ; Проверка режима копирования координат активной записи класса #12.
TryNearby:      LD A, R
                BIT 1, A
                JP Z, @Action.ScheduleSpawn.BuildPosition                       ; переход, если считанный бит 1 регистра R сброшен

                CALL @Action.FindRecordByCode.Entry
                LD A, (#9B83)
                AND A
                JP Z, @Action.ScheduleSpawn.BuildPosition                       ; переход, если #9B83 равен нулю

                LD A, (IX + @FActionRecord.ClassCode)
                CP #00
                JP Z, @Action.ScheduleSpawn.BuildPosition                       ; переход, если создаваемая запись имеет класс 0

                CP #05
                JP NC, @Action.ScheduleSpawn.BuildPosition                      ; переход, если создаваемая запись имеет класс не ниже 5

                LD D, #12
                CALL @Action.FindRecordByCode.Entry
                JR Z, @Action.ScheduleSpawn.BuildPosition                       ; переход, если поиск записи класса #12 завершился без совпадения

                LD L, (IY+#00)
                LD H, (IY+#01)
                LD (IX+#00), L
                LD (IX+#01), H
                LD L, (IY+#02)
                LD H, (IY+#03)
                LD A, R
                AND #01
                INC A
                LD D, A
                LD E, #80
                ADD HL, DE
                LD (IX+#02), L
                LD (IX+#03), H
                LD L, (IY+#04)
                LD H, (IY+#05)
                LD (IX+#04), L
                LD (IX+#05), H
                LD (IX + @FActionRecord.Unknown0A), #01
                LD (IX+#07), #40
                LD (IX+#08), #00
                LD (IX+#09), #00
                JP @Action.FinishSpawnRecord.InitParameters

                ; Чтение трёх знаковых компонент исходного вектора и выделение модулей.
BuildPosition:  LD HL, (#9B70)
                LD DE, (#9B73)
                LD BC, (#9B76)
                BIT 7, H
                JR Z, @Action.ScheduleSpawn.AbsSecond                           ; переход, если первая компонента неотрицательна

                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
AbsSecond:      BIT 7, D
                JR Z, @Action.ScheduleSpawn.AbsThird                            ; переход, если вторая компонента неотрицательна

                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
AbsThird:       BIT 7, B
                JR Z, @Action.ScheduleSpawn.ScaleWords                          ; переход, если третья компонента неотрицательна

                LD A, C
                CPL
                LD C, A
                LD A, B
                CPL
                LD B, A
                INC BC
                ; Сдвиг модулей в порядке HL, DE, BC до первого установленного старшего бита.
ScaleWords:     SLA L
                RL H
                JP M, @Action.ScheduleSpawn.RestoreFirst                        ; переход, если после сдвига установлен бит 15 первого модуля

                SLA E
                RL D
                JP M, @Action.ScheduleSpawn.RestoreSecond                       ; переход, если после сдвига установлен бит 15 второго модуля

                SLA C
                RL B
                JP P, @Action.ScheduleSpawn.ScaleWords                          ; переход, если после сдвига бит 15 третьего модуля сброшен

                RR B
                RR C
                AND A
RestoreSecond:  RR D
                RR E
                AND A
                ; Откат последнего сдвига затронутых компонент и снятие бита #0200.
RestoreFirst:   RR H
                RR L
                RES 1, B
                RES 1, D
                RES 1, H
                LD A, (#9B71)
                AND A
                JP P, @Action.ScheduleSpawn.SignSecond                          ; переход, если исходная первая компонента неотрицательна

                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
SignSecond:     LD A, (#9B74)
                AND A
                JP P, @Action.ScheduleSpawn.SignThird                           ; переход, если исходная вторая компонента неотрицательна

                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
SignThird:      LD A, (#9B77)
                AND A
                JP P, @Action.ScheduleSpawn.JitterPosition                      ; переход, если исходная третья компонента неотрицательна

                LD A, C
                CPL
                LD C, A
                LD A, B
                CPL
                LD B, A
                INC BC
                ; Прибавление знаковых случайных поправок из потоков 4, 1 и 5.
JitterPosition: PUSH BC
                PUSH DE
                PUSH HL
                CALL @Action.NextRandomWord4.Entry
                LD A, H
                AND #0F
                JR NZ, @Action.ScheduleSpawn.SignJitter0                        ; переход, если младшая тетрада старшего байта первой поправки ненулевая

                OR #07
SignJitter0:    BIT 7, H
                JR Z, @Action.ScheduleSpawn.StorePosition0                      ; переход, если исходное слово первой поправки неотрицательно

                CPL
StorePosition0: LD H, A
                POP DE
                ADD HL, DE
                LD (IX+#00), L
                LD (IX+#01), H
                CALL @Action.NextRandomWord1.Entry
                LD A, H
                AND #0F
                JR NZ, @Action.ScheduleSpawn.SignJitter1                        ; переход, если младшая тетрада старшего байта второй поправки ненулевая

                OR #07
SignJitter1:    BIT 7, H
                JR Z, @Action.ScheduleSpawn.StorePosition1                      ; переход, если исходное слово второй поправки неотрицательно

                CPL
StorePosition1: LD H, A
                POP DE
                ADD HL, DE
                LD (IX+#02), L
                LD (IX+#03), H
                CALL @Action.NextRandomWord5.Entry
                LD A, H
                AND #03
                JR NZ, @Action.ScheduleSpawn.SignJitter2                        ; переход, если два младших бита старшего байта третьей поправки ненулевые

                OR #01
SignJitter2:    BIT 7, H
                JR Z, @Action.ScheduleSpawn.StorePosition2                      ; переход, если исходное слово третьей поправки неотрицательно

                CPL
StorePosition2: LD H, A
                POP DE
                ADD HL, DE
                LD (IX+#04), L
                LD (IX+#05), H
                LD (IX + @FActionRecord.Unknown0A), #01
                CALL @Action.NextRandomWord5.Entry
                LD A, L
                AND #07
                LD L, A
                LD A, (#688B)
                OR A
                JR Z, @Action.FinishSpawnRecord.Entry                           ; переход, если число доступных целей равно нулю

                LD H, A
                LD A, L
                ; Деление индекса на два до попадания в доступный диапазон.
ReduceIndex:    CP H
                JR C, @Action.ScheduleSpawn.SelectTarget                        ; переход, если индекс строго меньше числа доступных целей

                SRL A
                JR @Action.ScheduleSpawn.ReduceIndex

                ; Сохранение индекса и вычисление адреса широкой цели с шагом 12 байтов.
SelectTarget:   LD (IX+#26), A
                LD IY, #9B1B
                LD DE, #000C
                LD B, A
                INC B
AdvanceTarget:  ADD IY, DE
                DJNZ @Action.ScheduleSpawn.AdvanceTarget

                CALL @Action.StepRecordTowardWideVector.Entry
                ; JP @Action.FinishSpawnRecord.Entry, продолжение в FinishSpawnRecord.asm

                endmodule
                endmodule
