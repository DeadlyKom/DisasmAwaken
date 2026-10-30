; -----------------------------------------
; запись 21, VOXAL.C
; логическая длина 3784, полный секторный размер 3840
; -----------------------------------------
                assert $ == #0000
                disp #EC00
                include "../Voxel/CreateSmallEffect.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #000E
                disp #EC0E
                include "../Voxel/ConfigureSmallEffect.asm"                     ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #001B
                disp #EC1B
                include "../Voxel/CreateLargeEffect.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0033
                disp #EC33
                include "../Voxel/AllocateEffect.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #007F
                disp #EC7F
                include "../Voxel/ClipSprite.asm"
                ent
                assert $ == #027A
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/21_VOXAL/Unclassified000.bin"
                assert $ == #0D31
                disp #F931
                include "../Voxel/Multiply7BitWord.asm"
                ent
                assert $ == #0D57
                disp #F957
                include "../Voxel/Divide7BitFixed.asm"
                ent
                assert $ == #0DE9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/21_VOXAL/Unclassified001.bin"
                assert $ == #0F00
