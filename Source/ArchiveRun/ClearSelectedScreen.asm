                module ArchiveRun
                module ClearSelectedScreen
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; заполнение выбранной страницы нулевым растром и атрибутами #07
                ; In:
                ;   в окне #C000 находится экранная страница
                ; Out:
                ;   растр очищен, #D800..#DB00 включительно заполнен #07
                ;   HL - #DB00, DE - #DB01, BC - 0
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; Note:
                ;   второй перенос записывает на один байт за областью атрибутов, штатный вход пока не найден
                ; -----------------------------------------
                ; заполнение растра и первой ячейки атрибутов перекрывающимся переносом
Entry:          LD HL, @ArchiveRunConst.Window
                LD D, H
                LD E, L
                INC DE
                LD (HL), #00
                LD BC, @ArchiveRunConst.BitmapBytes
                LDIR

                ; размножение атрибута с исходным захватом байта #DB00
                LD (HL), @ArchiveRunConst.BlankAttribute
                LD BC, @ArchiveRunConst.AttributeBytes
                LDIR
                RET

                endmodule
                endmodule
