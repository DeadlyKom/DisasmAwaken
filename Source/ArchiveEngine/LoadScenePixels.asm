                module ArchiveEngine
                module LoadScenePixels
                ; Документация [загрузка растра сцены](../../Docs/Scene1PixelPairs.md#код-во-внекаталожных-секторах)
                ; -----------------------------------------
                ; чтение scene1po в фиксированную память перед разбиением по страницам
                ; In:
                ;   TR-DOS и диск доступны, RAM #7700..#BFF3 свободна для рабочего растра
                ; Out:
                ;   18676 логических байтов файла по #7700, статус по #5D0F, прерывания запрещены
                ; Corrupt:
                ;   HL, DE, BC, AF, дополнительно состояние TR-DOS согласно ПЗУ
                ; -----------------------------------------
                ; перенос исходного ключа без терминатора в буфер TR-DOS
Entry:          LD HL, @ArchiveSceneKey.Value
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR

                ; чтение файла с явно заданным адресом назначения
                LD C, @TrDos.LoadFile
                LD A, @ArchiveEngineConst.LoadByName
                LD HL, @ArchiveEngineConst.ScenePixels
                CALL @TrDos.Dispatch
                DI
                RET

                endmodule
                endmodule
