                module ArchiveEngine
                module RunCombatScene
                ; Документация [запуск и цикл ENGINE](../../Docs/ArchiveEngineStartup.md)
                ; -----------------------------------------
                ; переход из загрузчика к инициализации и основному циклу сцены
                ; In:
                ;   PC установлен загрузчиком по #4000, MemoryMode содержит 0..2
                ;   TR-DOS доступен, прерывания переданы в режиме загрузчика
                ; Out:
                ;   обычного возврата нет, исполнение повторяется с Frame
                ; Corrupt:
                ;   состояние процессора и памяти передаётся сцене, договор сохранения регистров отсутствует
                ; Note:
                ;   вход заменяет стек предыдущего меню, в конце таймера IRQ запрещает прерывания и останавливается
                ; -----------------------------------------
                ; установка собственного стека сцены и расчёт маски парной записи
Entry:          LD SP, @ArchiveEngineConst.SceneStackTop
                LD HL, @ArchiveFighters.First
                LD A, HIGH(@ArchiveFighters.Second)
                XOR H
                LD (@ArchiveOpponentMask.Value.High), A
                LD A, LOW(@ArchiveFighters.Second)
                XOR L
                LD (@ArchiveOpponentMask.Value.Low), A

                ; выбор селектора по настройке меню и запись его адреса в операнд JP
                LD A, (@ArchiveEngineState.MemoryMode)
                LD E, A
                LD D, #00
                LD HL, @ArchiveEnginePages.Targets
                ADD HL, DE
                ADD HL, DE
                LD E, (HL)
                INC HL
                LD D, (HL)
                LD (@ArchiveEngine.SelectPage.Dispatch + 1), DE

                ; подготовка пустого экрана, файлов и состояния первого кадра
                CALL @ArchiveEngine.ClearShadowScreen.Entry
                CALL @ArchiveEngine.LoadCombatResources.Entry
                CALL @ArchiveEngine.PrepareCombatScene.Entry
                CALL @ArchiveEngine.EnableSceneInterrupts.Entry

                ; применение ввода и обновление кадров обоих бойцов
Frame:          CALL @ArchiveEngine.ApplyCombatInput.Entry
                CALL @ArchiveEngine.AdvanceFighterFrames.Entry
                CALL @ArchiveEngine.FrameHook.Entry
                CALL @ArchiveEngine.ApplyFighterFrames.Entry
                CALL @ArchiveEngine.ReconcileCombatView.Entry
                ; восстановление прежнего фона, наложение и вывод нового кадра
                CALL @ArchiveEngine.RestoreCombatFrame.Entry
                CALL @ArchiveEngine.ComposeCombatFrame.Entry
                CALL @ArchiveEngine.ShowViewport.Entry
                JP @ArchiveEngine.RunCombatScene.Frame

                endmodule
                endmodule
