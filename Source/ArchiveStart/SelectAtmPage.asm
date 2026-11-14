                module ArchiveStart
                module SelectAtmPage
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; переключение страницы ATM-2 стандартным и расширенным портами
                ; In:
                ;   AF - A, логический код, поле Visible содержит бит показа
                ;   ROM TR-DOS допускает вывод через #2A53
                ; Out:
                ;   #7FFD получает младший номер и бит показа, #FFF7 получает (NOT код) OR #C0
                ;   HL и DE восстановлены
                ; Corrupt:
                ;   BC, AF, отображение страниц
                ; -----------------------------------------
                ; сохранение пар и формирование младшего номера страницы
Entry:          PUSH HL
                PUSH DE
                LD (@ArchiveStartData.Page.CurrentCode), A
                PUSH AF
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
                POP AF

                ; инверсия полного кода и вывод через ROM
                LD BC, @ArchiveEngineConst.AtmWindowPort
                CPL
                SET 6, A
                SET 7, A
                CALL @ArchiveStart.OutputThroughDos.Entry
                POP DE
                POP HL
                RET

                endmodule
                endmodule
