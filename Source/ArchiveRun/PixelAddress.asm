                module ArchiveRun
                module PixelAddress
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; перевод пиксельных координат в адрес растра ZX Spectrum
                ; In:
                ;   DE - D, строка Y, E, пиксель X
                ; Out:
                ;   HL - адрес байта растра в области #4000, A - X AND 7
                ; Corrupt:
                ;   HL, AF
                ; -----------------------------------------
                ; перестановка битов Y и X для расчёта младшего байта
Entry:          LD A, D
                RRCA
                RRCA
                RRCA
                LD H, A
                XOR E
                AND #07
                XOR E
                RRCA
                RRCA
                RRCA
                LD L, A

                ; расчёт старшего байта и выделение бита внутри знакоместа
                LD A, D
                XOR H
                AND #07
                XOR H
                AND #1F
                OR #40
                LD H, A
                LD A, E
                AND #07
                RET

                endmodule
                endmodule
