                module ArchiveStart
                module ShowScreen
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; выбор видимой и отображённой в окне экранной страницы
                ; In:
                ;   AF - A, экран 0 или 1
                ; Out:
                ;   Visible хранит новый экран, выбрана страница 5 или 7
                ; Corrupt:
                ;   BC, AF, отображение страниц
                ; -----------------------------------------
                ; сохранение видимого экрана и вычисление кода его страницы
Entry:          LD (@ArchiveStartData.Page.Visible), A
                SLA A
                OR @ArchiveStartConst.FirstScreenPage
                JP @ArchiveStart.SelectPage.Dispatch

                endmodule
                endmodule
