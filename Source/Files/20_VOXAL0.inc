; -----------------------------------------
; запись 20, VOXAL0.C
; логическая длина 11264, полный секторный размер 11264
; -----------------------------------------
                assert $ == #0000
                assert $ == #0000
                disp #C000
                include "../Voxel/Data/Palette.asm"
                ent
                assert $ == #0400
                disp #C400
                include "../Voxel/Data/LargeEffectFrames.asm"
                ent
                assert $ == #1800
                disp #D800
                include "../Voxel/Data/SmallEffectFrames.asm"
                ent
                assert $ == #21C0
                ; Назначение следующих 832 байтов ещё не установлено.
                incbin "../Resources/20_VOXAL0/AfterSmallFrames.bin"
                assert $ == #2500
                disp #E500
                include "../Voxel/RotateBasisVectors.asm"
                ent
                assert $ == #28A1
                disp #E8A1
                include "../Voxel/SignedSeededProduct.asm"
                ent
                assert $ == #2965
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/20_VOXAL0/Unclassified001.bin"
                assert $ == #2C00
