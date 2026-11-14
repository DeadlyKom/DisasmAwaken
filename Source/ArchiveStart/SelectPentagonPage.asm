                module ArchiveStart
                module SelectPentagonPage
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; выбор страницы Pentagon одним значением #7FFD
                ; In:
                ;   AF - A, логический код, Visible содержит бит показа
                ; Out:
                ;   младшие три бита задают номер, бит 3 кода становится битом 6 порта
                ;   бит показа берётся из Visible, выбранная ROM кодируется #10
                ; Corrupt:
                ;   BC, AF, отображение страниц
                ; -----------------------------------------
                ; сохранение логического кода и перенос разряда расширения
Entry:          LD (@ArchiveStartData.Page.CurrentCode), A
                PUSH AF
                AND #08
                SLA A
                SLA A
                SLA A
                LD B, A
                POP AF

                ; соединение расширения с младшими тремя разрядами
                AND #07
                OR B
                LD B, A

                ; добавление бита показа и запись итогового байта #7FFD
                LD A, (@ArchiveStartData.Page.Visible)
                SLA A
                SLA A
                SLA A
                OR @ArchiveStartConst.BaseRomBit
                OR B
                LD BC, @Hardware.PagingPort
                OUT (C), A
                RET

                endmodule
                endmodule
