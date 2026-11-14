                module ArchiveStart
                module LoadBankFile
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; перенос ключа и загрузка одного BANK в окно #C000
                ; In:
                ;   HL - адрес девятибайтового ключа, страница назначения выбрана
                ; Out:
                ;   NextKey указывает на следующий ключ, TR-DOS возвращает статус по #5D0F
                ; Corrupt:
                ;   HL, DE, BC, AF, дополнительно состояние TR-DOS согласно ПЗУ
                ; -----------------------------------------
                ; копирование ключа и сохранение следующего адреса до вызова ROM
Entry:          LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD (@ArchiveStartLoadState.Value.NextKey), HL

                ; чтение логических байтов файла в выбранное окно
                LD HL, @ArchiveStartConst.Window
                LD A, @ArchiveStartConst.LoadByName
                LD C, @TrDos.LoadFile
                CALL @TrDos.Dispatch
                RET

                endmodule
                endmodule
