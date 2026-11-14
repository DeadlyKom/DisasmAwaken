                module ArchiveStart
                module SelectBankIndex
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; преобразование индекса файла BANK в логический код страницы
                ; In:
                ;   AF - A, индекс 0..5
                ; Out:
                ;   A получает код 8..13 и исполнение продолжается в SelectPage.Dispatch
                ; Corrupt:
                ;   HL, BC, AF
                ; -----------------------------------------
                ; индексация таблицы шести кодов
Entry:          LD HL, @ArchiveStartData.Page.Bank0
                LD C, A
                LD B, #00
                ADD HL, BC
                LD A, (HL)

                ; JP SelectPage.Dispatch, продолжение в SelectPage.asm

                endmodule
                endmodule
