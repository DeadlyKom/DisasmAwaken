                module ArchiveRun
                module RunMenu
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; подготовка двух экранов и кадровый опрос клавиш архивного меню
                ; In:
                ;   RUN загружен по #6000, доступны страницы 5 и 7
                ; Out:
                ;   обычного возврата нет, подтверждение Start передаёт управление загрузчику
                ; Corrupt:
                ;   состояние передаётся меню, исходные регистры и стек не сохраняются
                ; -----------------------------------------
                ; установка стека и чёрного бордюра
Entry:          DI
                LD SP, @ArchiveRunConst.StackTop
                XOR A
                OUT (#FE), A

                ; копирование обоих исходных экранов в страницы 5 и 7
                LD A, #00
                CALL @ArchiveRun.SetVisibleScreen.Entry
                LD HL, @ArchiveRunImages.MainScreen
                CALL @ArchiveRun.CopyScreen.Entry
                LD A, #01
                CALL @ArchiveRun.SetVisibleScreen.Entry
                LD HL, @ArchiveRunImages.ShadowScreen
                CALL @ArchiveRun.CopyScreen.Entry

                ; вывод начального списка, стрелки выбора и подготовка IRQ
                LD HL, @ArchiveRunMenus.MainCount
                CALL @ArchiveRun.RenderMenu.Entry
                CALL @ArchiveRun.ToggleSelectionMarker.Entry
                CALL @ArchiveRun.EnableMenuInterrupts.Entry

                ; ожидание кадра и смена видимого экрана
FrameWait:      HALT
                LD A, (@ArchiveRunState.Visible)
                XOR #01
                CALL @ArchiveRun.SetVisibleScreen.Entry

                ; сброс кода действия кадра и проверка Caps Shift
                LD E, #00
                LD BC, #FEFE
                IN A, (C)
                BIT 0, A
                JR Z, @ArchiveRun.RunMenu.CursorKeys                            ; переход, если нажат Caps Shift, проверить клавиши курсора

                ; проверка 9 и 8 в строке цифр
                LD BC, #EFFE
                IN A, (C)
                BIT 1, A
                CALL Z, @ArchiveRun.MoveSelectionUp.Entry                       ; вызов, если нажата 9, выбрать предыдущий пункт
                BIT 2, A
                CALL Z, @ArchiveRun.MoveSelectionDown.Entry                     ; вызов, если нажата 8, выбрать следующий пункт

                ; проверка 0 для подтверждения
ConfirmZero:    BIT 0, A
                CALL Z, @ArchiveRun.InvokeSelection.Entry                       ; вызов, если нажат 0, выполнить выбранный пункт

                ; проверка Enter
                LD BC, #BFFE
                IN A, (C)
                BIT 0, A
                CALL Z, @ArchiveRun.InvokeSelection.Entry                       ; вызов, если нажат Enter, выполнить выбранный пункт

                ; проверка Q и W для движения к предыдущему пункту
                LD BC, #FBFE
                IN A, (C)
                BIT 0, A
                CALL Z, @ArchiveRun.MoveSelectionUp.Entry                       ; вызов, если нажата Q, выбрать предыдущий пункт
                BIT 1, A
                CALL Z, @ArchiveRun.MoveSelectionUp.Entry                       ; вызов, если нажата W, выбрать предыдущий пункт

                ; проверка A и S для движения к следующему пункту
                LD BC, #FDFE
                IN A, (C)
                BIT 0, A
                CALL Z, @ArchiveRun.MoveSelectionDown.Entry                     ; вызов, если нажата A, выбрать следующий пункт
                BIT 1, A
                CALL Z, @ArchiveRun.MoveSelectionDown.Entry                     ; вызов, если нажата S, выбрать следующий пункт

                ; проверка Space для подтверждения
                LD BC, #7FFE
                IN A, (C)
                BIT 0, A
                CALL Z, @ArchiveRun.InvokeSelection.Entry                       ; вызов, если нажат Space, выполнить выбранный пункт

                ; запись последнего кода действия для блокировки удерживаемой клавиши
                LD A, E
                LD (@ArchiveRunState.LastKey), A
                JR @ArchiveRun.RunMenu.FrameWait

                ; проверка цифровых курсоров при удержании Caps Shift
CursorKeys:     LD BC, #EFFE
                IN A, (C)
                BIT 3, A
                CALL Z, @ArchiveRun.MoveSelectionUp.Entry                       ; вызов, если нажата 7 вместе с Caps Shift, выбрать предыдущий пункт
                BIT 4, A
                CALL Z, @ArchiveRun.MoveSelectionDown.Entry                     ; вызов, если нажата 6 вместе с Caps Shift, выбрать следующий пункт
                JR @ArchiveRun.RunMenu.ConfirmZero

                endmodule
                endmodule
