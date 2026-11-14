                module ArchiveStart
                module RestoreLayerStack
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; общий выход из трёх исполняемых растровых слоёв
                ; In:
                ;   операнд LD SP содержит стек вызова слоя
                ; Out:
                ;   SP восстановлен, выполнен возврат к вызвавшей слой процедуре
                ; Corrupt:
                ;   SP возвращается к обычному договору CALL
                ; -----------------------------------------
Entry:          LD SP, #0000
                RET

                endmodule
                endmodule
