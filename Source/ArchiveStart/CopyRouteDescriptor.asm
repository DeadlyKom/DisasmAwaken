                module ArchiveStart
                module CopyRouteDescriptor
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; выбор и копирование описания маршрута для двух селекторов
                ; In:
                ;   HL - адрес младшего селектора, DE - назначение, AF - A, старший селектор
                ; Out:
                ;   записаны 50 байтов маршрута 4 × старший + младший, HL и DE указывают за скопированными байтами
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
                ; вычисление номера маршрута из двух селекторов
Entry:          ADD A, A
                ADD A, A
                ADD A, (HL)
                LD C, A
                LD B, #00

                ; чтение указателя из таблицы слов
                LD HL, @ArchiveStartRoutePointers.Variant00
                ADD HL, BC
                ADD HL, BC
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A

                ; копирование физической записи маршрута
                LD BC, @FArchiveBankStripRoute
                LDIR
                RET

                endmodule
                endmodule
