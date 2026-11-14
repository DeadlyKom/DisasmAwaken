                module ArchiveEngine
                module SelectPage
                ; Документация [выбор страниц](../../Docs/ArchiveEnginePaging.md)
                ; -----------------------------------------
                ; сохранение кода страницы и вызов выбранного при запуске селектора
                ; In:
                ;   AF - A, логический код страницы, штатные значения 0..15
                ;   операнд Dispatch содержит адрес аппаратного селектора
                ; Out:
                ;   AF - A, значение последнего OUT, флаги по правилам выбранного селектора
                ;   State.CurrentCode содержит исходный A целиком, BC и SP восстановлены
                ; Corrupt:
                ;   AF, отображение банкового окна
                ; Note:
                ;   в режиме ATM-2 второй OUT выполняется из ROM TR-DOS
                ; -----------------------------------------
Entry:          LD (@ArchiveEnginePages.State.CurrentCode), A
                PUSH BC
Dispatch:       JP #0000                                                        ; исходный ноль, адрес записывает RunCombatScene

                endmodule
                endmodule
