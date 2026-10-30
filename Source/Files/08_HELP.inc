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
                include "../Help/FormatNumber.asm"
                ent
                assert $ == #007C
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/08_HELP/Unclassified000.bin"
                assert $ == #1800
