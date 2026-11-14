                module ArchiveStart
                module CommitRightRoute
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; подключение правого маршрута после смены селектора или при запуске меню
                ; In:
                ;   селекторы обеих сторон заданы, окно #C000 содержит рабочий код и таблицы START
                ; Out:
                ;   маски трёх слоёв пересчитаны, описание правого маршрута скопировано, первый буфер готов
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, временно меняется отображение страниц
                ; -----------------------------------------
                ; вычисление координат правого варианта и выбор завершающей пары масок
Entry:          LD HL, (@ArchiveStartData.Frame.RightMinor)
                CALL @ArchiveStart.CalculateLayerOrigin.Entry
                LD HL, @ArchiveStartConst.RightCoordSkip
                LD (@ArchiveStart.ApplyLayerMasks.EndPairPatch + 1), HL

                ; пересчёт масок с выделением слоя этой стороны
                LD HL, @ArchiveStartLayerPrograms.Second.Entry
                CALL @ArchiveStart.RebuildLayerMasks.Entry

                ; выбор и копирование 50-байтового описания маршрута
                LD A, (@ArchiveStartData.Frame.RightMajor)
                LD HL, @ArchiveStartData.Frame.RightMinor
                LD DE, @ArchiveStartRoutes.Right
                CALL @ArchiveStart.CopyRouteDescriptor.Entry

                ; сброс готовности и установка индекса #FF перед подготовкой первого буфера
                XOR A
                LD (@ArchiveStart.StageRightStrip.Entry + 1), A
                DEC A
                LD (@ArchiveStartRoutes.RightIndex), A
                CALL @ArchiveStart.StageRightStrip.Entry

                ; разрешение вывода полосы в кадровом обработчике
                XOR A
                LD (@ArchiveStart.HandleBankFrame.SkipRight + 1), A
                RET

                endmodule
                endmodule
