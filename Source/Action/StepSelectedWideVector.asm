                module Action
                module StepSelectedWideVector
                ; Документация [алгоритм и проверка](../../Docs/ActionWideVectorState.md)
                ; -----------------------------------------
                ; Шаг кодов движения к выбранному широкому вектору и проверка следующих состояний
                ; исходная запись 17, адреса F0BE..F0F7
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, альтернативные регистры учитываются договорами дочерних процедур
                ;   IX указывает FActionRecord с Components, OffsetPhase1/2, TargetCodeStep, Unknown26, StateCode и ClassCode
                ;   Unknown26 задаёт индекс строки из трёх dword по 9B27+12*индекс, доступны фактические байты выбранной строки
                ;   действуют договоры StepRecordTowardWideVector, CheckLinkedTargetTransition и NextRandomWord2
                ;   ACTION банка 0 и таблицы геометрии доступны, 18 дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены
                ; Out:
                ;   перед переходами состояния всегда выполнен StepRecordTowardWideVector с IY выбранной строки
                ;   CheckLinkedTargetTransition может установить связь и State0E либо выполнить переходы State13/14, Carry немедленно ведёт к общему F0F8
                ;   при Carry=0 дополнительный поток 2 вызывается только при ненулевом байте 9B83 и полном ClassCode в диапазоне 1..4
                ;   только H нового слова потока 2=41 и L>=5A устанавливают StateCode=0C, это не маскированная проверка класса
                ;   HL, DE, BC, AF и альтернативные HL/DE/BC определяются последним реально вызванным дочерним алгоритмом и проверенными порогами
                ;   AF', IX, I/IM/IFF сохраняются, IY определяется выбранным вектором либо поиском кандидата, итоговый 7FFD=10
                ;   PC=F0F8 и внешний SP сохраняется, общий хвост не включён в данный договор
                ;   R учитывает все M1 выбора строки и дочерних путей, выбор требует 6+3*(Unknown26+1) M1 до первого CALL
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IY, R, коды движения и условно поля состояний, связи и таймера, состояния потоков, изменяемые операнды дочерних процедур, CPU-стек, 7FFD
                ; Note:
                ;   при Unknown26=FF исходный INC B даёт ноль, DJNZ выполняет 256 сложений, строка находится по A71B, ограничение диапазона не добавлялось
                ;   выбор не проверяет границы логического массива, старшие индексы могут читать другие физические данные, их назначение этим не переопределяется
                ;   69632 сценария включают все пары входного R и полного класса, все 256 индексов, режимы и обе границы случайного перехода
                ;   сверены точные регистры, флаги, R, восемь банков, кратность RAM-записей, остатки стека и настоящие OUT дочерней геометрии
                ;   основная проверка использует пустой список кандидатов, самостоятельный договор CheckLinkedTargetTransition проверен отдельно
                ;   полное произведение входов, общий F0F8, аппаратные IRQ, сборка, точные T и нативный запуск не проверялись
                ; -----------------------------------------
                ; Выбор строки широкого вектора по Unknown26, индекс FF сохраняет исходные 256 итераций DJNZ.
Entry:          LD B, (IX + @FActionRecord.Unknown26)
                INC B
                ; Подготовка адреса перед первой строкой и физического размера трёх dword.
                LD IY, @ActionWideStateConst.BeforeFirst
                LD DE, @ActionWideStateConst.VectorStride
                ; Расчёт адреса очередной строки прибавлением её исходного размера.
SelectVector:   ADD IY, DE
                DJNZ @Action.StepSelectedWideVector.SelectVector

                ; Обновление кодов движения через исходное насыщение, банковый корень и оба кодировщика отношения.
                CALL @Action.StepRecordTowardWideVector.Entry
                ; Проверка случайного выбора связи либо фазовых переходов после изменения кодов движения.
                CALL @Action.CheckLinkedTargetTransition.Entry
                JP C, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если дочерняя проверка вернула Carry, продолжить общий расчёт смещений

                ; Проверка глобального допуска дополнительного перехода State0C.
                LD A, (@ActionWideStateConst.ModeByte)
                AND A
                JR Z, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если байт допуска равен нулю, продолжить общий расчёт смещений

                ; Проверка полного ClassCode, дополнительный переход разрешён только классам от 1 до 4.
                LD A, (IX + @FActionRecord.ClassCode)
                CP #00
                JR Z, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если ClassCode равен нулю, продолжить общий расчёт смещений

                CP @ActionWideStateConst.FirstExcluded
                JR NC, @Action.PrepareObjectOffsetTransform.Entry               ; переход, если ClassCode не меньше пяти, продолжить общий расчёт смещений

                ; Обновление отдельного случайного потока 2 после всех предварительных допусков.
                CALL @Action.NextRandomWord2.Entry
                ; Проверка точного старшего байта нового слова перед проверкой нижнего порога.
                LD A, H
                CP @ActionWideStateConst.RandomHigh
                JR NZ, @Action.PrepareObjectOffsetTransform.Entry               ; переход, если старший байт нового слова не равен 41, продолжить общий расчёт смещений

                ; Проверка нижней границы младшего байта при уже принятом старшем байте 41.
                LD A, L
                CP @ActionWideStateConst.RandomLowMin
                JR C, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если младший байт меньше 5A, сохранить состояние и продолжить общий расчёт смещений

                ; Обновление StateCode до 0C после совпадения обоих случайных условий.
                LD (IX + @FActionRecord.StateCode), @ActionWideStateConst.NextState
                ; JP @Action.PrepareObjectOffsetTransform.Entry, продолжение в PrepareObjectOffsetTransform.asm

                endmodule
                endmodule
