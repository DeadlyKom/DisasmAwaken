                module ArchiveEngine
                module SelectPentagonPage
                ; Документация [выбор страниц](../../Docs/ArchiveEnginePaging.md)
                ; -----------------------------------------
                ; преобразование логического кода страницы в значение порта Pentagon
                ; In:
                ;   AF - A, логический код, BC сохранён переходником SelectPage на стеке
                ; Out:
                ;   AF - A, #18 OR (код AND #07) OR ((код AND #08) << 3), флаги последнего OR
                ;   BC восстановлен, выбран теневой экран, отправлено одно значение в #7FFD
                ; Corrupt:
                ;   AF
                ; -----------------------------------------
                ; перенос четвёртого разряда кода в разряд 6 порта #7FFD
Entry:          LD C, A
                AND @ArchiveEngineConst.ExtendedPage
                SLA A
                SLA A
                SLA A
                LD B, A

                ; объединение номера страницы и режима показа
                LD A, C
                AND @ArchiveEngineConst.LowPageMask
                OR B
                LD BC, @Hardware.PagingPort
                OR @ArchiveEngineConst.ScreenRomBits
                OUT (C), A
                POP BC
                RET

                endmodule
                endmodule
