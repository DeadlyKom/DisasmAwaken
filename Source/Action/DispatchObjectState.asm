                module Action
                module DispatchObjectState
                ; Документация [алгоритм и проверка](../../Docs/ActionObjectStateDispatch.md)
                ; -----------------------------------------
                ; Выбор состояния объекта, косвенный вызов обработчика и последующее обновление записи
                ; исходная запись 17, код ACTION банка 0, смещения #97C6..#9865
                ; In:
                ;   AF, A передаёт разность только на входе StoreRemainder, IX указывает запись
                ;   R участвует в выборе перехода, банк 0 выбран, на стеке доступны слова рамки обработчика
                ;   для обычного игрового вызова состояние выбирает существующий обработчик таблицы, IRQ не вмешиваются
                ; Out:
                ;   по входу и классу выбирается байт состояния, LinkFlags обнуляется
                ;   вызов выполняется по слову таблицы с исходным байтовым удвоением состояния, на стеке возврат ResumeUpdate и сохранённый IX
                ;   при штатном возврате обработчика IX восстанавливается, выполняется PrepareRecordScale и управление передаётся обходчику по F735
                ; Corrupt:
                ;   HL, DE, BC, AF, R, поля записи и стек, далее изменения зависят от выбранного обработчика и обновления
                ; Note:
                ;   входы и точный выбор проверены до первой инструкции цели, состояние за пределами таблицы не считается допустимым
                ;   возврат проверен с настоящим обновлением для всех классов и исходных чётных указателей
                ;   отдельно проверен полный возврат трёх фазовых обработчиков на записи с маркером доступности, прочие цели разбираются отдельно
                ; -----------------------------------------
                ; Проверка класса перед начальной установкой состояния.
Entry:          LD A, (IX + @FActionRecord.ClassCode)
                CP #12
                JP Z, @Action.SetClass18ObjectState.Entry                       ; переход, если класс равен #12, назначить состояние #0A

                CP #10
                JR NC, @Action.DispatchObjectState.CallHandler                  ; переход, если класс не меньше #10, сохранить состояние

                LD A, (IX + @FActionRecord.Unknown0A)
                CP #07
                JP Z, @Action.DispatchObjectState.CallHandler                   ; переход, если состояние #07 нужно сохранить

                CP #06
                JP Z, @Action.DispatchObjectState.CallHandler                   ; переход, если состояние #06 нужно сохранить

                LD (IX + @FActionRecord.Unknown0A), #05
                JP @Action.DispatchObjectState.CallHandler

                ; Запись остатка после вычитания порога и проверка класса.
StoreRemainder: LD (IX + @FActionRecord.Unknown13), A
                LD A, (IX + @FActionRecord.ClassCode)
                CP #10
                JP NC, @Action.DispatchObjectState.CallHandler                  ; переход, если класс не меньше #10, сохранить состояние

                LD A, (IX + @FActionRecord.Unknown0A)
                CP #02
                JP NZ, @Action.DispatchObjectState.CheckState                   ; переход, если состояние отличается от #02

                LD C, (IX + @FActionRecord.LinkedIndex)
                INC C
                JR Z, @Action.DispatchObjectState.ChooseThreshold               ; переход, если индекс связи равен #FF, проверить смену состояния

                LD A, R
                CP #0A
                JR C, @Action.DispatchObjectState.ChooseThreshold               ; переход, если прочитанное R меньше #0A, проверить смену состояния

                JP @Action.DispatchObjectState.CallHandler

                ; Проверка диапазонов состояний, допускающих замену.
CheckState:     CP #04
                JP C, @Action.DispatchObjectState.ChooseThreshold               ; переход, если состояние ниже #04, проверить смену

                CP #0A
                JP C, @Action.DispatchObjectState.CallHandler                   ; переход, если состояние от #04 до #09, сохранить его

                ; Выбор порога R по младшей тетраде класса.
ChooseThreshold:LD A, (IX + @FActionRecord.ClassCode)
                AND #0F
                CP #03
                LD C, #70
                JP Z, @Action.DispatchObjectState.CheckTransition               ; переход, если класс #03 использует порог #70

                CP #00
                LD C, #75
                JP Z, @Action.DispatchObjectState.CheckTransition               ; переход, если класс #00 использует порог #75

                CP #01
                LD C, #50
                JP Z, @Action.DispatchObjectState.CheckTransition               ; переход, если класс #01 использует порог #50

CheckTransition:LD A, (IX + @FActionRecord.Unknown0A)
                CP #07
                JR Z, @Action.DispatchObjectState.CallHandler                   ; переход, если текущее состояние #07 сохраняется

                CP #06
                JR Z, @Action.DispatchObjectState.CallHandler                   ; переход, если текущее состояние #06 сохраняется

                LD A, R
                CP C
                LD A, #02
                JR C, @Action.DispatchObjectState.StoreState                    ; переход, если R ниже порога, записать состояние #02

                LD A, #05
StoreState:     LD (IX + @FActionRecord.Unknown0A), A
                ; Сброс LinkFlags и чтение слова таблицы по удвоенному коду состояния.
CallHandler:    LD (IX + @FActionRecord.LinkFlags), #00
                LD A, (IX + @FActionRecord.Unknown0A)
                SLA A
                LD L, A
                LD H, #00
                LD DE, @ActionObjectStateHandlers.State00.Handler
                ADD HL, DE
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                ; Сохранение IX и создание возврата для косвенного перехода.
                PUSH IX
                LD DE, @Action.DispatchObjectState.ResumeUpdate
                PUSH DE
                JP (HL)

                ; Восстановление IX после обработчика и вызов обновления компонент.
ResumeUpdate:   POP IX
                CALL @Action.PrepareRecordScale.Entry
                JP @Action.UpdateObjects.PointF735

                endmodule
                endmodule
