                module Action
                module SpawnPeriodicClass3Record
                ; Документация [алгоритм и проверка](../../Docs/ActionPeriodicClass3State.md)
                ; -----------------------------------------
                ; Периодическое создание одной записи класса 3 с уменьшением родительского счётчика и обязательным сбросом баз
                ; исходная запись 17, адреса F3F0..F49B
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает активную FActionRecord родителя
                ;   Unknown0D задаёт обычный байтовый индекс связанной записи, SavedStateCode используется здесь как счётчик оставшихся созданий
                ;   SpawnPhase доступен для изменения, от A100 достижим маркер либо свободная запись, слово координат по 9BC1 читается классификатором
                ;   действуют договоры FindReusableRecord, RecordIndexToAddress, ClassifyCoordinateRegion и ResetRecordUpdateBases
                ;   ACTION банка 0 выбран, два дополнительных байта CPU-стека доступны, IRQ и повторный вход исключены
                ; Out:
                ;   SpawnPhase получает wrap8(SpawnPhase+1) AND 0F, только нулевой результат допускает попытку создания
                ;   при ненулевой фазе либо отсутствии свободной записи новая запись не создаётся, Base0..2 всё равно обнуляются
                ;   при найденной свободной записи проверяется Component0.High записи по индексу Unknown0D, значение 80 переводит родителя в StateCode=09 без заполнения ребёнка
                ;   иначе ребёнок получает компоненты 0 и 2 родителя, компоненту 1 плюс BC, B=1 либо 2 по R и C=80
                ;   ClassCode ребёнка=3, ModelOffset=10+4*код ClassifyCoordinateRegion слова по 9BC1, остальные записываемые поля перечислены в документации
                ;   после заполнения SavedStateCode родителя уменьшен на один по модулю 256, только переход 1 в 0 устанавливает родительский StateCode=09
                ;   на всех путях HL=0, Base0..2=0, прочие выходы зависят от последнего исполненного ребёнка
                ;   при создании DE=0040, BC содержит смещение второй компоненты, A равен декрементированному родительскому счётчику и F от DEC с Carry=0
                ;   HL', DE', BC', AF', IX, I/IM/IFF и paging сохраняются, IY равен найденной записи либо маркеру после поиска и исходному IY без поиска
                ;   SP после внешнего RET увеличен на два, дополнительная рамка равна двум байтам, точная стоимость R приведена по ветвям в документации
                ; Corrupt:
                ;   HL, DE, BC, AF, IY, R, SpawnPhase, ReuseByte просмотренных свободных записей, условные поля родителя и ребёнка, Base0..2 и два временных байта CPU-стека, SP внешним RET
                ; Note:
                ;   SpawnPhase общий для всех вызывающих записей, период измеряется вызовами этой процедуры, не гарантированным числом кадров
                ;   SavedStateCode в этом состоянии является счётчиком, его прежнее нулевое значение оборачивается в FF, универсальное значение поля не выдумывается
                ;   135168 сценариев охватили все фазы и родительские счётчики, все слова координат классификатора и граничные индексы со всеми R
                ;   реальные поиск, индекс, классификатор и сброс исполняются, сверены регистры, флаги, R, восемь банков и все записи до полного RET
                ;   полное произведение входов, аппаратные IRQ, точные T, сборка и нативный запуск не выполнялись
                ; -----------------------------------------
                ; Обновление общей фазы допуска, после INC остаются только четыре младших бита.
Entry:          LD A, #0A
                INC A
                AND @ActionPeriodicClass3Const.PhaseMask
                LD (@ActionPeriodicClass3State.SpawnPhase), A
                JP NZ, @Action.ResetRecordUpdateBases.Entry                     ; переход, если новая SpawnPhase ненулевая, пропустить создание и обнулить общие базы

                ; Поиск свободной записи, его очистка ReuseByte сохраняется даже при последующем отказе связанной записи.
                CALL @Action.FindReusableRecord.Entry
                JP Z, @Action.ResetRecordUpdateBases.Entry                      ; переход, если поиск достиг маркера, обнулить базы без создания ребёнка

                ; Преобразование обычного индекса из Unknown0D, отдельной обработки FF здесь нет.
                LD A, (IX + @FActionRecord.Unknown0D)
                CALL @Action.RecordIndexToAddress.Entry
                ; Проверка старшего байта Component0 связанной записи перед заполнением найденного свободного слота.
                INC L
                LD A, (HL)
                CP @ActionReuseConst.ReusableHigh
                JR NZ, @Action.SpawnPeriodicClass3Record.CreateChild            ; переход, если связанная запись имеет Component0.High не равный 80, заполнить ребёнка

                ; Обновление родителя до состояния 09 при недоступной связи, найденный свободный слот не заполняется.
                LD (IX + @FActionRecord.StateCode), @ActionPeriodicClass3Const.ParentState
                JP @Action.ResetRecordUpdateBases.Entry

                ; Копирование первой компоненты родителя в ребёнка без числового изменения.
CreateChild:    LD L, (IX + @FActionRecord.Components.Component0.Low)
                LD H, (IX + @FActionRecord.Components.Component0.High)
                LD (IY + @FActionRecord.Components.Component0.Low), L
                LD (IY + @FActionRecord.Components.Component0.High), H
                ; Расчёт положительного смещения второй компоненты, B равен младшему биту прочитанного R плюс один, C=80.
                LD A, R
                AND #01
                INC A
                LD B, A
                LD C, #80
                ; Создание второй компоненты ребёнка прибавлением общего BC по модулю 65536.
                LD L, (IX + @FActionRecord.Components.Component1.Low)
                LD H, (IX + @FActionRecord.Components.Component1.High)
                ADD HL, BC
                LD (IY + @FActionRecord.Components.Component1.Low), L
                LD (IY + @FActionRecord.Components.Component1.High), H
                ; Копирование третьей компоненты родителя без смещения.
                LD L, (IX + @FActionRecord.Components.Component2.Low)
                LD H, (IX + @FActionRecord.Components.Component2.High)
                LD (IY + @FActionRecord.Components.Component2.Low), L
                LD (IY + @FActionRecord.Components.Component2.High), H
                ; Классификация исходного слова координат по 9BC1 для выбора одного из четырёх байтовых смещений модели.
                LD HL, (@ActionPeriodicRegionState.Coordinate)
                CALL @Action.ClassifyCoordinateRegion.Entry
                ; Расчёт ModelOffset=10+4*код области, повороты безопасны для доказанного диапазона кода 0..3.
                RLCA
                RLCA
                ADD A, @ActionPeriodicClass3Const.ModelBase
                LD (IY + @FActionRecord.ModelOffset), A
                ; Заполнение исходных управляющих полей ребёнка класса 3, не записываемые поля свободного слота сохраняются.
                LD (IY + @FActionRecord.TargetIndex), @ActionPeriodicClass3Const.TargetLife
                LD (IY + @FActionRecord.OffsetPhase0), @ActionPeriodicClass3Const.InitialPhase0
                LD (IY + @FActionRecord.OffsetPhase1), #00
                LD (IY + @FActionRecord.OffsetPhase2), #00
                LD (IY + @FActionRecord.Unknown11), @ActionPeriodicClass3Const.TimerByte11
                LD (IY + @FActionRecord.StateCode), @ActionPeriodicClass3Const.InitialState
                LD (IY + @FActionRecord.SavedStateCode), @ActionPeriodicClass3Const.SavedState
                LD (IY + @FActionRecord.LinkFlags), #00
                LD (IY + @FActionRecord.ClassCode), @ActionPeriodicClass3Const.ChildClass
                LD (IY + @FActionRecord.Unknown14), #00
                ; Копирование индекса связи Unknown0D родителя в LinkedIndex ребёнка и завершение его управляющих полей.
                LD A, (IX + @FActionRecord.Unknown0D)
                LD (IY + @FActionRecord.Unknown15), #FF
                LD (IY + @FActionRecord.LinkedIndex), A
                LD (IY + @FActionRecord.Unknown13), @ActionPeriodicClass3Const.ControlByte13
                LD (IY + @FActionRecord.Unknown10), @ActionPeriodicClass3Const.InitialByte10
                LD (IY + @FActionRecord.TargetCodeStep), @ActionChildSpawnConst.TargetStep
                ; Обновление счётчика числа созданий, физическое поле SavedStateCode имеет в этом состоянии числовую роль.
                LD A, (IX + @FActionRecord.SavedStateCode)
                DEC A
                LD (IX + @FActionRecord.SavedStateCode), A
                JR NZ, @Action.SpawnPeriodicClass3Record.ResetBases             ; переход, если декрементированный счётчик ненулевой, сохранить текущее состояние родителя

                ; Обновление родителя до состояния 09 после последнего разрешённого создания.
                LD (IX + @FActionRecord.StateCode), @ActionPeriodicClass3Const.ParentState
                ; Обязательное обнуление общих Base0..2 через исходный хвост с внешним RET.
ResetBases:     JP @Action.ResetRecordUpdateBases.Entry

                endmodule
                endmodule
