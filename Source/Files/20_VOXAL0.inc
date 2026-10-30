; -----------------------------------------
; запись 20, VOXAL0.C
; логическая длина 11264, полный секторный размер 11264
; -----------------------------------------
                assert $ == #0000
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/20_VOXAL0/Unclassified000.bin"
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
