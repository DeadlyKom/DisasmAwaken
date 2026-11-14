                module ArchiveRun
                module FindModeCaption
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; поиск адреса подписи режима по двухбайтовой таблице
                ; In:
                ;   AF - A, номер режима 0..2
                ; Out:
                ;   DE и IX - адрес подписи, это же слово записано в ModeItem.Caption
                ; Corrupt:
                ;   HL, DE, AF, IX
                ; -----------------------------------------
                ; расчёт индекса слова и сохранение адреса в записи меню
Entry:          ADD A, A
                LD E, A
                LD D, #00
                LD HL, @ArchiveRunMenus.PentagonText
                ADD HL, DE
                LD E, (HL)
                INC HL
                LD D, (HL)
                LD IXH, D
                LD IXL, E
                LD (@ArchiveRunMenus.ModeItem.Caption), DE
                RET

                endmodule
                endmodule
