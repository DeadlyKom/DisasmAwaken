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
                ; Исходный хвост HIPERJMP.van после 13 кадров телепорта
                ; Документация [разметка VOXAL0](../../Docs/VoxelPhysicalResources.md)
                incbin "../Voxel/Resources/TeleportResourceTail.bin"
                assert $ == #2500
                disp #E500
                include "../Voxel/RotateBasisVectors.asm"
                ent
                assert $ == #28A1
                disp #E8A1
                include "../Voxel/SignedSeededProduct.asm"
                ent
                assert $ == #2965
                ; Заполнение ADRXX00 перед исходной таблицей CSTB.dat
                ; Документация [выравнивание таблицы](../../Docs/VoxelBasisRotation.md)
                incbin "../Voxel/Resources/CosineTableAlignment.bin"
                assert $ == #2A00
                disp #EA00
                include "../Voxel/Data/CosineLow.asm"
                ent
                assert $ == #2B00
                disp #EB00
                include "../Voxel/Data/CosineHigh.asm"
                ent
                assert $ == #2C00
