                module ArchiveStart
                module SelectScreenForDraw
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; выбор страницы для рисования без изменения видимого экрана
                ; In:
                ;   AF - A, индекс экранной страницы 0 или 1
                ; Out:
                ;   в окне страница 5 или 7, Visible сохранён
                ; Corrupt:
                ;   BC, AF, отображение страниц
                ; -----------------------------------------
                ; вычисление номера страницы при прежнем бите показа
Entry:          SLA A
                OR @ArchiveStartConst.FirstScreenPage
                JP @ArchiveStart.SelectPage.Dispatch

                endmodule
                endmodule
