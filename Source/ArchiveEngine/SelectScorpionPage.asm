                module ArchiveEngine
                module SelectScorpionPage
                ; Документация [выбор страниц](../../Docs/ArchiveEnginePaging.md)
                ; -----------------------------------------
                ; запись дополнительного разряда страницы Scorpion перед основным портом
                ; In:
                ;   AF - A, логический код, BC сохранён переходником SelectPage на стеке
                ; Out:
                ;   AF - A, #18 OR (код AND #07), флаги последнего OR
                ;   BC восстановлен, разряд 3 кода записан в разряд 4 порта #1FFD
                ; Corrupt:
                ;   AF
                ; -----------------------------------------
                ; запись дополнительного разряда с сохранением исходного кода
Entry:          PUSH AF
                AND @ArchiveEngineConst.ExtendedPage
                SLA A
                LD BC, @ArchiveEngineConst.ScorpionPort
                OUT (C), A
                POP AF

                ; выбор младших трёх разрядов и режима показа через #7FFD
                AND @ArchiveEngineConst.LowPageMask
                LD BC, @Hardware.PagingPort
                OR @ArchiveEngineConst.ScreenRomBits
                OUT (C), A
                POP BC
                RET

                endmodule
                endmodule
