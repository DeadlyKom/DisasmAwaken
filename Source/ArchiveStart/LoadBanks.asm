                module ArchiveStart
                module LoadBanks
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; последовательная загрузка BANK0..BANK5 в выбранные страницы
                ; In:
                ;   селектор страниц настроен, TR-DOS доступен
                ; Out:
                ;   при успехе все шесть страниц содержат исходные файлы, NextKey указывает за таблицу
                ;   A равен 6 и B равен нулю
                ; Corrupt:
                ;   HL, DE, BC, AF, отображение страниц и состояние TR-DOS
                ; Note:
                ;   каждый новый запрос следует без проверки статуса предыдущего
                ; -----------------------------------------
                ; установка начального индекса, счётчика и указателя таблицы
Entry:          LD B, @ArchiveStartConst.BankCount
                XOR A
                LD HL, @ArchiveStartBankKeys.Bank0
                LD (@ArchiveStartLoadState.Value.NextKey), HL

                ; сохранение индекса и выбор страницы очередного файла
NextBank:       PUSH BC
                PUSH AF
                CALL @ArchiveStart.SelectBankIndex.Entry
                LD HL, (@ArchiveStartLoadState.Value.NextKey)
                CALL @ArchiveStart.LoadBankFile.Entry

                ; восстановление счётчиков и переход к следующему индексу
                POP AF
                POP BC
                INC A
                DJNZ @ArchiveStart.LoadBanks.NextBank

                RET

                endmodule
                endmodule
