                module ArchiveRun
                module CopyScreen
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; перенос 6912 байтов растра и атрибутов в выбранную страницу
                ; In:
                ;   HL - адрес полного снимка экрана
                ; Out:
                ;   HL - адрес за снимком, DE - #DB00, BC - 0
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
Entry:          LD DE, @ArchiveRunConst.Window
                LD BC, @ArchiveRunConst.ScreenBytes
                LDIR
                RET

                endmodule
                endmodule
