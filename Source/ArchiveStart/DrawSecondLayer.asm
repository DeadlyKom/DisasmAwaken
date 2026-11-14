                module ArchiveStart
                module DrawSecondLayer
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; исполнение команд растрового вывода второго слоя
                ; In:
                ;   экранная страница выбрана, операнд конца слоя указывает на RestoreLayerStack
                ; Out:
                ;   выведены 168 строк растра шириной 20 байтов, SP восстановлен общим выходом
                ; Corrupt:
                ;   HL, DE, AF, временно SP
                ; Note:
                ;   JR и CALL внутри растрового блока отсутствуют, возврат через изменённый JP
                ; -----------------------------------------
                ; сохранение SP и передача управления растровому блоку
Entry:          LD (@ArchiveStart.RestoreLayerStack.Entry + 1), SP
                JP @ArchiveStartLayerPrograms.Second.Entry

                endmodule
                endmodule
