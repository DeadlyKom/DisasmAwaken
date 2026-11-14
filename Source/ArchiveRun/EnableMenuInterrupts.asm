                module ArchiveRun
                module EnableMenuInterrupts
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; заполнение таблицы IM2 и подключение кадрового обработчика меню
                ; In:
                ;   прерывания ещё запрещены после входа RUN
                ; Out:
                ;   I=#5E, IM 2, прерывания разрешены после RET
                ;   таблица #5E00..#5F00 ведёт на #5F5F, там записан JP MenuInterrupt
                ; Corrupt:
                ;   HL, DE, BC, AF, I, IM и IFF
                ; -----------------------------------------
                ; заполнение 257 байтов одинаковым значением для всех значений шины
Entry:          LD HL, @ArchiveRunConst.VectorBase
                LD D, H
                LD E, L
                INC DE
                LD (HL), @ArchiveRunConst.VectorFill
                LD BC, @ArchiveRunConst.VectorTail
                LDIR

                ; запись переходника и включение нового режима IRQ
                LD A, #C3
                LD (@ArchiveRunConst.VectorJump), A
                LD HL, @ArchiveRun.MenuInterrupt.Entry
                LD (@ArchiveRunConst.VectorOperand), HL
                LD A, @ArchiveRunConst.VectorPage
                LD I, A
                IM 2
                EI
                RET

                endmodule
                endmodule
