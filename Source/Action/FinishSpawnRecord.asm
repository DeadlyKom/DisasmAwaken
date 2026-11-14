                module Action
                module FinishSpawnRecord
                ; Документация [алгоритм и проверка](../../Docs/ActionSpawnRecordFinish.md)
                ; -----------------------------------------
                ; Заполнение параметров новой записи и передача диспетчеру класса
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #2011..#20D9
                ; In:
                ;   IX указывает создаваемую запись, класс, модель и начальное состояние уже заданы
                ;   доступны потоки случайных слов 12, 13 и состояние потока 3, OBJECT3D находится в странице 4
                ;   SpawnField11, SpawnValueMask и SpawnValueCap являются изменяемыми операндами, ApplyParameterSet задаёт их полями 0E, 0C и 0D
                ; Out:
                ;   Entry обнуляет байт 07, InitParameters заполняет поля по классу, потоку и R
                ;   ReadHeader может вызываться отдельно, байт 25 получает 1 при показателе 4, иначе 2
                ;   передача в DispatchRecordClass без нового возврата, настоящий SP сохранён, выбрана страница 0
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', R, поля записи, потоки, временные слова и 7FFD
                ; Note:
                ;   пересечение масок #55 и #2A равно нулю, поле 11 на основном пути получает SpawnField11, исходно 20
                ;   кандидат поля 13 равен L OR SpawnValueMask, при кандидате не меньше SpawnValueCap записывается cap-1 по модулю 256
                ;   исходные mask=32 и cap=64 дают min(99,L OR 32), изменяемый cap=00 даёт FF, класс 8 позже заменяет поле 13 на F0
                ;   последовательные проверки класса #06 и #07 используют тот же A, специальные записи между ними и StoreState недостижимы
                ; -----------------------------------------
                ; Сброс первого байта смещения перед инициализацией.
Entry:          LD (IX + @FActionRecord.OffsetPhase0), #00
                ; Продвижение потока 12, непересекающиеся маски оставляют изменяемый SpawnField11.
InitParameters: CALL @Action.NextRandomWord12.Entry
                LD A, L
                AND #55
                LD L, A
                LD A, H
                AND #2A
                AND L
                ; Подстановка SpawnField11, исходно 20, поле 0E ApplyParameterSet меняет операнд.
                OR #20
                LD (IX + @FActionRecord.Unknown11), A
                LD (IX + @FActionRecord.LinkFlags), #00
                LD (IX + @FActionRecord.MissileRepeatDelay), #00
                LD (IX + @FActionRecord.LinkOverride), #FF
                LD (IX + @FActionRecord.LinkedIndex), #FF
                LD HL, (@ActionRandomStreams.Stream3.LowWord)
                LD (IX + @FActionRecord.Phase0OrLink), L
                LD (IX + @FActionRecord.LocalPhase1), H
                ; Получение параметров из потока 13 и проверка верхней границы.
                CALL @Action.NextRandomWord13.Entry
                LD E, H
                LD A, L
                ; Расчёт кандидата через SpawnValueMask и чтение SpawnValueCap, исходно 32 и 64.
                OR #32
                LD H, #64
                CP H
                JR C, @Action.FinishSpawnRecord.StoreLimit                      ; переход, если кандидат меньше текущего SpawnValueCap, сохранить кандидата

                LD A, H
                DEC A
StoreLimit:     LD (IX + @FActionRecord.EffectReserve), A
                LD A, E
                OR #A0
                LD (IX + @FActionRecord.ReserveCeiling), A
                LD A, #20
                LD (IX + @FActionRecord.OffsetScaleLow), A
                XOR A
                LD (@ActionRandomStreams.Stream3.FoldByte), A
                LD A, (IX + @FActionRecord.ClassCode)
                CP #08
                JR NZ, @Action.FinishSpawnRecord.CheckClassSix                  ; переход, если класс отличается от #08, сохранить общие поля

                LD (IX + @FActionRecord.EffectReserve), #F0
                LD (IX + @FActionRecord.ReserveCeiling), #FA
                LD A, (IX + @FActionRecord.OffsetPhase0)
                LD (IX + @FActionRecord.Phase0OrLink), A
                LD A, (IX + @FActionRecord.OffsetPhase1)
                LD (IX + @FActionRecord.LocalPhase1), A
                LD A, (IX + @FActionRecord.OffsetPhase2)
                LD (IX + @FActionRecord.Phase2OrTarget), A
CheckClassSix:  LD A, (IX + @FActionRecord.ClassCode)
                CP #06
                JR NZ, @Action.FinishSpawnRecord.StoreState                     ; переход, если класс отличается от #06

                CP #07
                JR NZ, @Action.FinishSpawnRecord.StoreState                     ; переход, если тот же класс отличается от #07, после предыдущей проверки переход всегда выполняется

                LD (IX + @FActionRecord.EffectReserve), #F0
                LD (IX + @FActionRecord.ReserveCeiling), #FA
                LD (IX + @FActionRecord.Unknown11), #6E
                LD (IX + @FActionRecord.OffsetScaleHigh), #00
                ; Сохранение начального состояния и выбор байта повторного использования по R.
StoreState:     LD A, (IX + @FActionRecord.StateCode)
                LD (IX + @FActionRecord.SavedStateCode), A
                LD A, R
                AND #0F
                INC A
                AND #0F
                LD C, A
                LD A, (IX + @FActionRecord.ClassCode)
                CP #08
                JR NZ, @Action.FinishSpawnRecord.StoreReuse                     ; переход, если класс отличается от #08, оставить исходную выборку

                LD A, R
                AND #40
                JR Z, @Action.FinishSpawnRecord.StoreReuse                      ; переход, если бит 6 второго чтения R сброшен, оставить исходную выборку

                SET 2, C
StoreReuse:     LD (IX + @FActionRecord.ReuseByte), C
                LD (IX + @FActionRecord.PhaseMoveTimer), #00
                LD (IX + @FActionRecord.ProximityIndex), #FF
                LD (IX + @FActionRecord.ProximityClass), #FF
                ; Чтение заголовка модели для выбора записываемого масштаба.
ReadHeader:     LD A, (IX + @FActionRecord.ModelOffset)
                CALL @Action.ReadObjectHeaderWord.Entry
                LD A, H
                CP #04
                LD A, #02
                JR NZ, @Action.FinishSpawnRecord.StoreScale                     ; переход, если показатель отличается от 4, записать 2

                DEC A
StoreScale:     LD (IX + @FActionRecord.TargetCodeStep), A
                JP @Action.DispatchRecordClass.Entry

                endmodule
                endmodule
