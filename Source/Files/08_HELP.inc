; -----------------------------------------
; запись 8, HELP.C
; логическая длина 5921, полный секторный размер 6144
; -----------------------------------------
                assert $ == #0000
                disp #DB00
                include "../Help/IndexTextLines.asm"
                ent
                assert $ == #0042
                disp #DB42
                include "../Help/PrintIndexedLine.asm"
                ent
                assert $ == #0057
                disp #DB57
                include "../Help/SelectText.asm"
                ent
                assert $ == #005B
                disp #DB5B
                include "../Help/PrintCrRecordAndRows.asm"
                ent
                assert $ == #007C
                disp #DB7C
                include "../Help/Data/LinePointers.asm"
                ent
                assert $ == #087C
                ; CR-заголовки разделов, потребитель PrintCrRecordAndRows, адрес E37C
                incbin "../Resources/08_HELP/SectionTitles.bin"
                assert $ == #08E2
                ; LF-записи справки, потребитель IndexTextLines, адрес E3E2
                incbin "../Resources/08_HELP/SectionTexts.bin"
                assert $ == #1721
                ; Unknown, секторный хвост после логической длины, исходные байты сохранены
                incbin "../Resources/08_HELP/SectorTail.bin"
                assert $ == #1800
