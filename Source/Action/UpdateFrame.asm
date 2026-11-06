                module Action
                module UpdateFrame
                ; Документация [пороговые и событийные ветки кадра](../../Docs/ActionFrameGates.md)
                ; Документация [банковые записи кадра](../../Docs/ActionBank4Writes.md)
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Обработка таймеров, управления, визуальных модулей и игровых объектов
; исходная запись 17, файловые смещения #485E..#4ACB
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          LD A, #00
                DEC A
                JP M, @Action.UpdateFrame.PointA867                             ; переход, если уменьшенный байт задержки отрицателен, оставить прежний операнд


                LD (#A85F), A
PointA867:      CALL @Action.ScheduleSpawn.Entry
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
                JR Z, @Action.UpdateFrame.PointA8B2                             ; переход, если признак близкой записи сброшен


                XOR A
                LD (@ActionCloseRecordState.InhibitCode), A
                LD A, (#A794)
                SUB #28
                JP C, @Action.ShowNoiseBeforeReload.Entry                       ; переход, если значение первой шкалы меньше 40


                LD (#A794), A
                LD A, #02
                LD (#664A), A
                ; Обновление третьей шкалы по переполнению накопителя фазы.
PointA8B2:      LD A, #00
                ADD A, #14
                LD (#A8B3), A
                JR NC, @Action.UpdateFrame.PointA8C8                            ; переход, если прибавление 20 к фазе не переполнило байт


                LD A, #00
                CP #2E
                JR NC, @Action.UpdateFrame.PointA8C8                            ; переход, если третья шкала уже достигла #2E


                INC A
                LD (#A8BC), A
                LD (#666B), A
PointA8C8:      CALL @Action.UpdateObjects.Entry
                XOR A
                LD (#A781), A
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
                JR Z, @Action.UpdateFrame.PointA928                             ; переход, если бит 0 сохранённой маски событий сброшен


                ; Запрос потока AY и выбор стоимости события по трём байтам.
                XOR A
                LD (#A78C), A
                LD HL, #EF22
                LD (#ECA9), HL
                LD B, #04
                LD A, (#9C1C)
                DEC B
                INC A
                JP NZ, @Action.UpdateFrame.PointA919                            ; переход, если первый байт отличается от #FF, стоимость равна 3


                LD A, (#9C1D)
                DEC B
                INC A
                JP NZ, @Action.UpdateFrame.PointA919                            ; переход, если второй байт отличается от #FF, стоимость равна 2


                LD A, (#9C1E)
                DEC B
                INC A
                JP NZ, @Action.UpdateFrame.PointA919                            ; переход, если третий байт отличается от #FF, стоимость равна 1


                LD B, #04
PointA919:      LD A, (#A794)
                SUB B
                JP C, @Action.ShowNoiseBeforeReload.Entry                       ; переход, если первая шкала меньше выбранной стоимости


                LD (#A794), A
                LD A, #01
                LD (#664A), A
PointA928:      BIT 1, C
                JR Z, @Action.UpdateFrame.PointA948                             ; переход, если бит 1 сохранённой маски событий сброшен


                ; Обновление фазы мигания, цвета и запроса второго потока AY.
                LD A, #80
                RRCA
                LD (#A92D), A
                LD A, #05
                JR NC, @Action.UpdateFrame.PointA93E                            ; переход, если прежний младший бит фазы мигания сброшен


                LD HL, #ED8F
                LD (#ECF6), HL
                LD A, #35
PointA93E:      LD (#5A1C), A
                XOR A
                LD (#A78C), A
                JP @Action.UpdateFrame.PointA94D


PointA948:      LD A, #05
                LD (#5A1C), A
PointA94D:      BIT 2, C
                JR Z, @Action.UpdateFrame.PointA965                             ; переход, если бит 2 сохранённой маски событий сброшен


                ; Списание 40 из первой шкалы при установленном бите 2.
                XOR A
                LD (#A78C), A
                LD A, (#A794)
                SUB #28
                JP C, @Action.ShowNoiseBeforeReload.Entry                       ; переход, если значение первой шкалы меньше 40


                LD (#A794), A
                LD A, #01
                LD (#664A), A
                ; Восстановление первой шкалы по переполнению отдельного накопителя фазы.
PointA965:      LD A, #00
                ADD A, #50
                LD (#A966), A
                JR NC, @Action.UpdateFrame.PointA97E                            ; переход, если прибавление 80 к фазе не переполнило байт


                LD A, (#A794)
                CP #2E
                JR NC, @Action.UpdateFrame.PointA97E                            ; переход, если первая шкала уже достигла #2E


                INC A
                LD (#A794), A
                LD A, #01
                LD (#664A), A
PointA97E:      CALL @Action.UpdateAyEffects.Entry
                ; Выбор банка 4 для трёх групп XOR 60 в OBJECT3D, совпадающие адреса ACTION банка 0 не меняются.
                LD A, #14
                CALL @Action.SelectMemoryPage.Entry
                LD A, (#D408)
                XOR #60
                LD (#D408), A
                LD A, (#D6CC)
                XOR #60
                LD (#D6CC), A
                LD (#D77A), A
                LD (#D7C1), A
                LD (#D82D), A
                LD (#DA61), A
                LD (#DA9E), A
                LD (#C09F), A
                LD (#C13A), A
                LD (#D138), A
                LD (#D1BA), A
                LD (#C1DC), A
                LD (#C2B8), A
                LD (#C301), A
                LD (#C370), A
                LD (#C3D5), A
                LD (#C44E), A
                LD (#C545), A
                LD (#C649), A
                LD (#C6B2), A
                LD (#D222), A
                LD (#C787), A
                LD (#C820), A
                LD (#C92F), A
                LD (#D3CF), A
                LD (#D3F9), A
                LD (#D3FE), A
                LD (#D53B), A
                LD (#CA96), A
                LD (#D67D), A
                LD (#CB9F), A
                LD (#CBA4), A
                LD (#CC77), A
                LD (#CCE5), A
                LD (#CD79), A
                LD (#CDC3), A
                LD (#CE28), A
                LD (#CE6C), A
                LD (#CE9D), A
                LD (#CF47), A
                LD (#CF9C), A
                LD (#CFEF), A
                LD (#D083), A
                LD (#D0C6), A
                LD (#D0CB), A
                LD (#D0D0), A
                LD (#D0D5), A
                LD A, (#D873)
                XOR #60
                LD (#D873), A
                LD (#D877), A
                LD (#D87B), A
                LD (#D87F), A
                LD (#D883), A
                LD (#D887), A
                LD (#D88B), A
                LD (#D88F), A
                LD (#C243), A
                LD (#C247), A
                LD (#C5CA), A
                LD (#C5E7), A
                LD (#C672), A
                LD (#C6AE), A
                LD (#D34D), A
                LD (#D355), A
                LD (#D359), A
                LD (#D2DE), A
                LD (#D2FD), A
                LD (#C733), A
                LD (#C765), A
                LD (#C9A2), A
                LD (#C9C4), A
                LD (#CA24), A
                LD (#CA2F), A
                LD (#D5C9), A
                LD (#D5D1), A
                LD (#CB29), A
                LD (#CB39), A
                LD (#CE0E), A
                LD (#CE1C), A
                LD (#D0F2), A
                LD (#D0F6), A
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.UpdatePanelGauges.Entry
                LD A, #00
                AND A
                LD A, #15
                JR NZ, @Action.UpdateFrame.PointAA96                            ; переход, если байт режима цвета ненулевой, записать #15


                LD A, #05
PointAA96:      LD (#5A1A), A
                LD A, #00
                DEC A
                EX AF, AF'
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                EX AF, AF'
                CALL NZ, @Controls.ToggleTargetOverlay.Entry                   ; вызов, если байт режима до DEC отличался от 1
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


PointAAC4:      LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                JP @Controls.RelocateStationReload.Entry


                endmodule
                endmodule
