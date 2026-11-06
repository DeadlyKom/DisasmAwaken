                module Action
                module CheckCloseRecordComponents
                ; Документация [три входа обработки записи](../../Docs/ActionCloseRecord.md)
                ; -----------------------------------------
                ; Дополнительный отбор по биту 4 ReuseByte и старшим байтам трёх компонент
                ; исходная запись 17, код ACTION банка 0, адреса E51F..E549
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX адрес читаемой FActionRecord
                ;   InhibitCode может быть любым байтом, этот вход не выполняет корневую проверку запрета и не загружает IX из альтернативного HL
                ;   действуют договоры ReverseCloseRecordState и TransferToStationLoader, банк 0 выбран, 7FFD не заблокирован, IRQ не вмешиваются
                ;   общий CPU-стек допускает четыре дополнительных байта
                ; Out:
                ;   при сброшенном бите 4 ReuseByte либо отказе любой компоненты исполнение переходит ReverseCloseRecordState
                ;   допуск компоненты проверяет старший байт, при его отрицательном знаке используется CPL без прибавления единицы
                ;   каждая из трёх компонент допускает старшие байты 00..03 и FC..FF, иные значения передают общий хвост инверсии
                ;   при установленном бите 4 и допуске всех трёх компонент HL и BC сохраняются, DE=0, AF=1193, SP входной, PC=DCE3 банка 1
                ;   IX, альтернативные регистры, IY, I, IM и IFF сохраняются в локальных границах, при инверсии SP увеличивается на два
                ;   ClassCode не фильтрует допуск передачи этого дополнительного входа, классы 11 и 14 не игнорируются автоматически
                ; Corrupt:
                ;   HL, DE, BC и AF по пути, R, временный CPU-стек до четырёх байтов, состояние общего хвоста при отказе, 7FFD при передаче
                ; Note:
                ;   внешний игровой вызывающий путь E51F пока не установлен, прямые сценарии модели доказывают локальный договор, а не его фактический вызов
                ;   проверка старших байтов не равна вычислению полного модуля слова и не заменяется NEG
                ;   после последнего условного JP возможен проход в соседний ReverseCloseRecordState, include имеют жёсткий порядок
                ; -----------------------------------------
                ; Проверка бита 4 ReuseByte дополнительного входа, это не корневая проверка ClassCode.
Entry:          BIT @ActionCloseRecordConst.ComponentBit, (IX + FActionRecord.ReuseByte)
                JR Z, @Action.ReverseCloseRecordState.Entry                     ; переход, если бит 4 ReuseByte сброшен, выполнить ReverseCloseRecordState

                ; Проверка старшего байта Component0, для отрицательного значения применяется только инверсия CPL.
                LD A, (IX + FActionRecord.Components.Component0.High)
                OR A
                JP P, @Action.CheckCloseRecordComponents.CheckComp0             ; переход, если старший байт Component0 неотрицателен, инверсию не выполнять

                CPL
                ; Проверка нормализованного старшего байта Component0 относительно HighLimit.
CheckComp0:     CP @ActionCloseRecordConst.HighLimit
                JR NC, @Action.ReverseCloseRecordState.Entry                    ; переход, если проверяемый старший байт Component0 не меньше 4, выполнить общий хвост

                ; Проверка старшего байта Component1 тем же преобразованием.
                LD A, (IX + FActionRecord.Components.Component1.High)
                OR A
                JP P, @Action.CheckCloseRecordComponents.CheckComp1             ; переход, если старший байт Component1 неотрицателен, инверсию не выполнять

                CPL
                ; Проверка нормализованного старшего байта Component1 относительно HighLimit.
CheckComp1:     CP @ActionCloseRecordConst.HighLimit
                JR NC, @Action.ReverseCloseRecordState.Entry                    ; переход, если проверяемый старший байт Component1 не меньше 4, выполнить общий хвост

                ; Проверка старшего байта Component2 тем же преобразованием.
                LD A, (IX + FActionRecord.Components.Component2.High)
                OR A
                JP P, @Action.CheckCloseRecordComponents.CheckComp2             ; переход, если старший байт Component2 неотрицателен, инверсию не выполнять

                CPL
                ; Проверка последней компоненты перед передачей следующему режиму.
CheckComp2:     CP @ActionCloseRecordConst.HighLimit
                JP C, @Action.TransferToStationLoader.Entry                     ; переход, если проверяемый старший байт Component2 меньше 4, выполнить TransferToStationLoader

                ; JP @Action.ReverseCloseRecordState.Entry, продолжение в ReverseCloseRecordState.asm

                endmodule
                endmodule
