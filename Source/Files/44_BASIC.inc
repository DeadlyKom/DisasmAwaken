                ; Единственная строка архивного BASIC и исходный хвост сектора.
                ; Документация [архивный вход BASIC](../../Docs/ArchiveMenuHandoff.md#строка-архивного-basic)
                assert $ == #0000
                disp #0000
                include "../Basic/Data/ArchiveRunLine.asm"
                ent
                assert $ == #001C
                disp #001C
                include "../Basic/Data/ArchiveAutostart.asm"
                ent
                assert $ == #0020
                incbin "../../Tools/Disasm/Extracted/Archived/44__K-II.d2.B.tail.bin", #0004, #00E0
                assert $ == #0100
