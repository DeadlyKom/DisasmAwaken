                module ArchiveStart
                module SelectScorpionPage
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; переключение страницы Scorpion двумя записями портов
                ; In:
                ;   AF - A, логический код, поле Visible содержит бит показа
                ; Out:
                ;   #1FFD получает бит 3 кода в разряде 4
                ;   #7FFD получает младшие три бита кода, бит показа и #10
                ; Corrupt:
                ;   BC, AF, отображение страниц
                ; -----------------------------------------
                ; сохранение кода и запись дополнительного разряда страницы
Entry:          LD (@ArchiveStartData.Page.CurrentCode), A
                PUSH AF
                AND #08
                SLA A
                LD BC, @ArchiveEngineConst.ScorpionPort
                OUT (C), A
                POP AF

                ; объединение младшего номера страницы с битом показа
                AND #07
                LD B, A
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
