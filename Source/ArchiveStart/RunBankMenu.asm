                module ArchiveStart
                module RunBankMenu
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; загрузка ресурсов, подключение меню BANK и основной цикл
                ; In:
                ;   START загружен по #6000, банк 0 содержит его продолжение от #C000
                ;   #5F5E содержит режим 0..2, TR-DOS доступен
                ; Out:
                ;   обычного возврата нет, рабочие маршруты и IRQ подключены
                ; Corrupt:
                ;   регистры, стек и отображение страниц переходят к меню
                ; -----------------------------------------
                ; настройка стека, чёрного бордюра и аппаратного селектора по коду RUN
Entry:          LD SP, @ArchiveStart.RunBankMenu.Entry
                XOR A
                OUT (#FE), A
                LD A, (@ArchiveStartConst.MemoryMode)
                ADD A, A
                LD E, A
                LD D, #00
                LD HL, @ArchiveStartModes.Targets
                ADD HL, DE
                LD E, (HL)
                INC HL
                LD D, (HL)
                LD (@ArchiveStart.SelectPage.Dispatch + 1), DE

                ; загрузка первого экрана в текущую экранную страницу
                LD A, (@ArchiveStartData.Page.NextVisible)
                CALL @ArchiveStart.ShowScreen.Entry
                LD HL, @ArchiveStartFileKeys.Choose1
                CALL @ArchiveStart.LoadChooseScreen.Entry

                ; загрузка второго экрана после переключения показа
                LD A, (@ArchiveStartData.Page.NextVisible)
                XOR #01
                CALL @ArchiveStart.ShowScreen.Entry
                LD HL, @ArchiveStartFileKeys.Choose2
                CALL @ArchiveStart.LoadChooseScreen.Entry

                ; запись адреса возврата перед тремя динамическими областями
                LD HL, @ArchiveStart.RestoreLayerStack.Entry
                LD (@ArchiveStartLayerPrograms.First.Restore + 1), HL
                LD (@ArchiveStartLayerPrograms.Second.Restore + 1), HL
                LD (@ArchiveStartLayerPrograms.Third.Restore + 1), HL

                ; загрузка шести BANK и возврат к рабочей странице меню
                CALL @ArchiveStart.LoadBanks.Entry
                XOR A
                OUT (#FE), A
                LD A, (@ArchiveStartData.Page.DefaultCode)
                CALL @ArchiveStart.SelectPage.Dispatch

                ; подключение двух маршрутов и кадрового прерывания
                CALL @ArchiveStart.CommitLeftRoute.Entry
                CALL @ArchiveStart.CommitRightRoute.Entry
                CALL @ArchiveStart.SetupInterrupts.Entry

                ; ожидание первого IRQ перед циклом
InitialHalt:    HALT

                ; подготовка полос и обработка клавиш в основном цикле
Frame:          CALL @ArchiveStart.StageLeftStrip.Entry
                CALL @ArchiveStart.StageRightStrip.Entry
                CALL @ArchiveStart.ScanLeftKeys.Entry
                CALL @ArchiveStart.ScanRightKeys.Entry
                JR @ArchiveStart.RunBankMenu.Frame

                endmodule
                endmodule
