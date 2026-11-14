                module ArchiveStart
                module SelectPage
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; переход к аппаратному селектору, выбранному настройкой RUN
                ; In:
                ;   AF - A, логический код страницы, адрес Dispatch уже записан
                ; Out:
                ;   выбрана страница, CurrentCode содержит полный исходный A
                ; Corrupt:
                ;   BC, AF, отображение страниц
                ; -----------------------------------------
Dispatch:       JP #0000

                endmodule
                endmodule
