                module Action
                module UpdateFrame
                ; Физическое состояние [панель и счётчик](../../Docs/ActionPanelPhysicalData.md)
                ; Внутренние входы [алгоритм](../../Docs/GraphicsStateInternalLabels.md)
                ; Документация [порядок вызовов кадра](../../Docs/ActionFlightCycle.md)
                ; Документация [пороговые и событийные ветки кадра](../../Docs/ActionFrameGates.md)
                ; Документация [банковые записи кадра](../../Docs/ActionBank4Writes.md)
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Обработка таймеров, управления, визуальных модулей и игровых объектов
; исходная запись 17, файловые смещения #485E..#4ACB
; In:
;   состояние задаётся StartFlight и предыдущими кадрами, при обычном входе выбрана страница #10
;   стек содержит возврат в MainLoop по #A85C, рабочие банки доступны
;   записи, состояния и ресурсы удовлетворяют договорам ScheduleSpawn, UpdateObjects и рисователей
;   IRQ не используют временные стеки рендереров, NMI не рассматривается
; Out:
;   обычный кадр возвращается со страницей #10, AF=#1042, DE=#0040, IX указывает маркер списка #8080
;   HL, BC, альтернативные регистры содержат результат DrawRadar, остальные значения определяются дочерними договорами
;   SP после RET равен входному SP+2, внешний возврат передаёт управление MainLoop
;   при переходе через шум к загрузке станции выбирается #11, SP кадра не снимается
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, IFF по дочерним вызовам
;   объекты, эффекты, рабочие векторы, экран, очередь, звук, таблицы OBJECT3D банка 4, операнды, стек и 7FFD
; Note:
;   64 полных кадра сверены с исходными вызовами, отдельный выход проверен до входа #4000
;   модели не исчерпывают все совместные состояния объектов, ввод, IRQ и нативный игровой процесс
; -----------------------------------------
Entry:          LD A, #00
                DEC A
                JP M, @Action.UpdateFrame.BeginScene                            ; переход, если уменьшенный байт задержки отрицателен, оставить прежний операнд


                LD (#A85F), A
BeginScene:     CALL @Action.ScheduleSpawn.Entry
                CALL @Action.ClearWorkBuffer.Entry
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL @Controls.XorBufferPoints.Entry
                CALL @Controls.TickBcdCounter.Entry
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.RenderSceneFrame.Entry
                CALL @Action.UpdateThirdGlyphVector.Entry
                ; Проверка двух порогов шкал и списание при установленном признаке близкой записи.
                LD A, #01
                LD (#E310), A
                LD A, (#6693)
                CP #2E
                JP NC, @Action.ShowNoiseBeforeReload.Entry                      ; переход, если пятая шкала достигла #2E


                LD A, (#6682)
                CP #2E
                JP NC, @Action.ShowNoiseBeforeReload.Entry                      ; переход, если четвёртая шкала достигла #2E


                LD A, (@ActionCloseRecordState.InhibitCode)
                AND A
                JR Z, @Action.UpdateFrame.StepGaugePhase                        ; переход, если признак близкой записи сброшен


                XOR A
                LD (@ActionCloseRecordState.InhibitCode), A
                LD A, (#A794)
                SUB #28
                JP C, @Action.ShowNoiseBeforeReload.Entry                       ; переход, если значение первой шкалы меньше 40


                LD (#A794), A
                LD A, #02
                LD (#664A), A
                ; Обновление фазы третьей шкалы, поле 05 ApplyParameterSet задаёт ThirdGaugeStep, исходно 14.
StepGaugePhase: LD A, #00
                ADD A, #14
                LD (#A8B3), A
                JR NC, @Action.UpdateFrame.UpdateRecords                        ; переход, если прибавление текущего ThirdGaugeStep не переполнило байт


                LD A, #00
                CP #2E
                JR NC, @Action.UpdateFrame.UpdateRecords                        ; переход, если третья шкала уже достигла #2E


                INC A
                LD (#A8BC), A
                LD (#666B), A
UpdateRecords:  CALL @Action.UpdateObjects.Entry
                ; Очистка старшего байта первого компонента особой родительской записи.
                XOR A
                LD (@ActionSpecialRecord.Value.Component0 + 1), A
                CALL @Action.SubtractScaledWorkVector.Entry
                CALL @Action.UpdateBodyMotion.Entry
                CALL @Action.UpdateVisualEffects.Entry
                CALL @Action.UpdateMotionFromControls.Entry
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL @Controls.UpdateBufferPoints.Entry
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.ApplyPendingRecordLink.Entry
                ; Сохранение исходной маски событий для трёх последовательных проверок.
                LD A, (#A78C)
                LD C, A
                BIT 0, C
                JR Z, @Action.UpdateFrame.CheckBlink                            ; переход, если бит 0 сохранённой маски событий сброшен


                ; Запрос потока AY и выбор стоимости события по трём байтам.
                XOR A
                LD (#A78C), A
                LD HL, #EF22
                LD (#ECA9), HL
                LD B, #04
                LD A, (@ActionShipEquipment.ShieldFortress.Value)
                DEC B
                INC A
                JP NZ, @Action.UpdateFrame.ApplyEventCost                       ; переход, если первый байт отличается от #FF, стоимость равна 3


                LD A, (@ActionShipEquipment.ShieldDefense1.Value)
                DEC B
                INC A
                JP NZ, @Action.UpdateFrame.ApplyEventCost                       ; переход, если второй байт отличается от #FF, стоимость равна 2


                LD A, (@ActionShipEquipment.ShieldDefense2.Value)
                DEC B
                INC A
                JP NZ, @Action.UpdateFrame.ApplyEventCost                       ; переход, если третий байт отличается от #FF, стоимость равна 1


                LD B, #04
ApplyEventCost: LD A, (#A794)
                SUB B
                JP C, @Action.ShowNoiseBeforeReload.Entry                       ; переход, если первая шкала меньше выбранной стоимости


                LD (#A794), A
                LD A, #01
                LD (#664A), A
CheckBlink:     BIT 1, C
                JR Z, @Action.UpdateFrame.ClearBlink                            ; переход, если бит 1 сохранённой маски событий сброшен


                ; Обновление фазы мигания, цвета и запроса второго потока AY.
                LD A, #80
                RRCA
                LD (#A92D), A
                LD A, #05
                JR NC, @Action.UpdateFrame.StoreBlink                           ; переход, если прежний младший бит фазы мигания сброшен


                LD HL, #ED8F
                LD (#ECF6), HL
                LD A, #35
StoreBlink:     LD (#5A1C), A
                XOR A
                LD (#A78C), A
                JP @Action.UpdateFrame.CheckDrain


ClearBlink:     LD A, #05
                LD (#5A1C), A
CheckDrain:     BIT 2, C
                JR Z, @Action.UpdateFrame.StepRegenPhase                        ; переход, если бит 2 сохранённой маски событий сброшен


                ; Списание 40 из первой шкалы при установленном бите 2.
                XOR A
                LD (#A78C), A
                LD A, (#A794)
                SUB #28
                JP C, @Action.ShowNoiseBeforeReload.Entry                       ; переход, если значение первой шкалы меньше 40


                LD (#A794), A
                LD A, #01
                LD (#664A), A
                ; Обновление фазы восстановления, поле 03 ApplyParameterSet задаёт RegenPhaseStep, исходно 50.
StepRegenPhase: LD A, #00
                ADD A, #50
                LD (#A966), A
                JR NC, @Action.UpdateFrame.BeginEffects                         ; переход, если прибавление текущего RegenPhaseStep не переполнило байт


                LD A, (#A794)
                CP #2E
                JR NC, @Action.UpdateFrame.BeginEffects                         ; переход, если первая шкала уже достигла #2E


                INC A
                LD (#A794), A
                LD A, #01
                LD (#664A), A
BeginEffects:   CALL @Action.UpdateAyEffects.Entry
                ; Выбор банка 4 для трёх групп заголовков граней OBJECT3D.
                ; [Физические поля и проверка банков](../../Docs/ActionBank4Writes.md)
                LD A, #14
                CALL @Action.SelectMemoryPage.Entry
                ; Переключение материала одной восьмиугольной грани.
                LD A, (@ActionModels.R13D5_04.Header)
                XOR @ActionPacketRendererConst.MaterialToggle
                LD (@ActionModels.R13D5_04.Header), A
                ; Переключение общего материала группы четырёхугольных граней.
                LD A, (@ActionModels.R1683_0C.Header)
                XOR @ActionPacketRendererConst.MaterialToggle
                LD (@ActionModels.R1683_0C.Header), A
                LD (@ActionModels.R16E0_1B.Header), A
                LD (@ActionModels.R1780_0A.Header), A
                LD (@ActionModels.R17DF_0D.Header), A
                LD (@ActionModels.R1A1E_0D.Header), A
                LD (@ActionModels.R1A6B_09.Header), A
                LD (@ActionModels.R0040_10.Header), A
                LD (@ActionModels.R00CC_11.Header), A
                LD (@ActionModels.R1103_07.Header), A
                LD (@ActionModels.R1150_11.Header), A
                LD (@ActionModels.R0167_14.Header), A
                LD (@ActionModels.R0271_0C.Header), A
                LD (@ActionModels.R02BE_0B.Header), A
                LD (@ActionModels.R0329_0B.Header), A
                LD (@ActionModels.R03AE_05.Header), A
                LD (@ActionModels.R03F1_10.Header), A
                LD (@ActionModels.R04B2_17.Header), A
                LD (@ActionModels.R0602_0A.Header), A
                LD (@ActionModels.R064F_0E.Header), A
                LD (@ActionModels.R11F9_04.Header), A
                LD (@ActionModels.R06EA_1E.Header), A
                LD (@ActionModels.R07C6_0D.Header), A
                LD (@ActionModels.R08A0_1A.Header), A
                LD (@ActionModels.R1398_08.Header), A
                LD (@ActionModels.R13D5_01.Header), A
                LD (@ActionModels.R13D5_02.Header), A
                LD (@ActionModels.R14BE_15.Header), A
                LD (@ActionModels.R0A40_09.Header), A
                LD (@ActionModels.R1622_10.Header), A
                LD (@ActionModels.R0B7A_02.Header), A
                LD (@ActionModels.R0B7A_03.Header), A
                LD (@ActionModels.R0C11_11.Header), A
                LD (@ActionModels.R0CA5_09.Header), A
                LD (@ActionModels.R0D10_11.Header), A
                LD (@ActionModels.R0D8B_09.Header), A
                LD (@ActionModels.R0DC9_0E.Header), A
                LD (@ActionModels.R0E36_07.Header), A
                LD (@ActionModels.R0E82_00.Header), A
                LD (@ActionModels.R0F11_06.Header), A
                LD (@ActionModels.R0F61_06.Header), A
                LD (@ActionModels.R0FA2_0E.Header), A
                LD (@ActionModels.R1047_09.Header), A
                LD (@ActionModels.R1089_0A.Header), A
                LD (@ActionModels.R1089_0B.Header), A
                LD (@ActionModels.R1089_0C.Header), A
                LD (@ActionModels.R1089_0D.Header), A
                ; Переключение общего материала группы треугольных граней.
                LD A, (@ActionModels.R1864_00.Header)
                XOR @ActionPacketRendererConst.MaterialToggle
                LD (@ActionModels.R1864_00.Header), A
                LD (@ActionModels.R1864_01.Header), A
                LD (@ActionModels.R1864_02.Header), A
                LD (@ActionModels.R1864_03.Header), A
                LD (@ActionModels.R1864_04.Header), A
                LD (@ActionModels.R1864_05.Header), A
                LD (@ActionModels.R1864_06.Header), A
                LD (@ActionModels.R1864_07.Header), A
                LD (@ActionModels.R0202_08.Header), A
                LD (@ActionModels.R0202_09.Header), A
                LD (@ActionModels.R056F_0A.Header), A
                LD (@ActionModels.R056F_10.Header), A
                LD (@ActionModels.R064F_00.Header), A
                LD (@ActionModels.R064F_0D.Header), A
                LD (@ActionModels.R1308_07.Header), A
                LD (@ActionModels.R1308_09.Header), A
                LD (@ActionModels.R1308_0A.Header), A
                LD (@ActionModels.R128A_0B.Header), A
                LD (@ActionModels.R128A_12.Header), A
                LD (@ActionModels.R06EA_0A.Header), A
                LD (@ActionModels.R06EA_16.Header), A
                LD (@ActionModels.R0935_11.Header), A
                LD (@ActionModels.R0935_18.Header), A
                LD (@ActionModels.R09F7_05.Header), A
                LD (@ActionModels.R09F7_08.Header), A
                LD (@ActionModels.R157E_0C.Header), A
                LD (@ActionModels.R157E_0E.Header), A
                LD (@ActionModels.R0B13_01.Header), A
                LD (@ActionModels.R0B13_05.Header), A
                LD (@ActionModels.R0DC9_08.Header), A
                LD (@ActionModels.R0DC9_0B.Header), A
                LD (@ActionModels.R10DB_02.Header), A
                LD (@ActionModels.R10DB_03.Header), A
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.UpdatePanelGauges.Entry
                LD A, #00
                AND A
                LD A, #15
                JR NZ, @Action.UpdateFrame.StorePanelAttr                       ; переход, если байт режима цвета ненулевой, записать #15


                LD A, #05
StorePanelAttr: LD (#5A1A), A
                ; Чтение режима отображения, 1 пропускает вызов, 2 выбирает короткие рамки, 3 полный проход.
OverlayMode:    LD A, #00
                DEC A
                EX AF, AF'
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                EX AF, AF'
                CALL NZ, @Controls.ToggleTargetOverlay.Entry                    ; вызов, если байт режима до DEC отличался от 1
                CALL @Controls.ConsumeTextQueue.Entry
                CALL @Controls.XorBufferMarker.Entry
                CALL @Controls.CopyViewportToScreen.Entry
                CALL @Controls.ConsumeTextQueue.Entry
                CALL @Controls.ConsumeTextQueue.Entry
                CALL @Controls.ConsumeTextQueue.Entry
                CALL @Controls.UpdateGlyphIndicators.Entry
                CALL @Controls.DrawRadar.Entry
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                RET


ReloadStation:  LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                JP @Controls.RelocateStationReload.Entry


                endmodule
                endmodule
