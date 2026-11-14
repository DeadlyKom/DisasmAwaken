                module ArchiveEngine
                module SelectAtmPage
                ; Документация [выбор страниц](../../Docs/ArchiveEnginePaging.md)
                ; -----------------------------------------
                ; переключение верхнего окна ATM-2 через два порта
                ; In:
                ;   AF - A, логический код, BC сохранён переходником SelectPage на стеке
                ;   ROM TR-DOS содержит переход через #3D2F к OUT (C), A по #2A53
                ; Out:
                ;   AF - A, (NOT код) OR #C0, флаги после CPL исходного A
                ;   HL и BC восстановлены, #7FFD получает младший номер и режим экрана
                ; Corrupt:
                ;   AF
                ; -----------------------------------------
                ; запись младшего номера и режима экрана в стандартный порт
Entry:          PUSH HL
                PUSH AF
                AND @ArchiveEngineConst.LowPageMask
                OR @ArchiveEngineConst.ScreenRomBits
                LD BC, @Hardware.PagingPort
                OUT (C), A
                POP AF

                ; инверсия кода страницы и установка двух старших разрядов для ATM-2
                LD BC, @ArchiveEngineConst.AtmWindowPort
                CPL
                SET @ArchiveEngineConst.AtmPortBit6, A
                SET @ArchiveEngineConst.AtmPortBit7, A
                CALL @ArchiveEngine.OutputThroughDos.Entry
                POP HL
                POP BC
                RET

                endmodule
                endmodule
