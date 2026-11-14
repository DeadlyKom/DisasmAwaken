                module ArchiveStart
                module CommitLeftRoute
                ; Документация [растровые слои](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; подключение левого маршрута после смены селектора или при запуске меню
                ; In:
                ;   селекторы обеих сторон заданы, окно #C000 содержит рабочий код и таблицы START
                ; Out:
                ;   маски трёх слоёв пересчитаны, описание левого маршрута скопировано, первый буфер готов
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, временно меняется отображение страниц
                ; -----------------------------------------
                ; вычисление координат левого варианта и выбор завершающей пары масок
Entry:          LD HL, (@ArchiveStartData.Frame.LeftMinor)
                CALL @ArchiveStart.CalculateLayerOrigin.Entry
                LD HL, #0000
                LD (@ArchiveStart.ApplyLayerMasks.EndPairPatch + 1), HL

                ; пересчёт масок с выделением слоя этой стороны
                LD HL, @ArchiveStartLayerPrograms.Third.Entry
                CALL @ArchiveStart.RebuildLayerMasks.Entry

                ; выбор и копирование 50-байтового описания маршрута
                LD A, (@ArchiveStartData.Frame.LeftMajor)
                LD HL, @ArchiveStartData.Frame.LeftMinor
                LD DE, @ArchiveStartRoutes.Left
                CALL @ArchiveStart.CopyRouteDescriptor.Entry

                ; сброс готовности и установка индекса #FF перед подготовкой первого буфера
                XOR A
                LD (@ArchiveStart.StageLeftStrip.Entry + 1), A
                DEC A
                LD (@ArchiveStartRoutes.LeftIndex), A
                CALL @ArchiveStart.StageLeftStrip.Entry

                ; разрешение вывода полосы в кадровом обработчике
                XOR A
                LD (@ArchiveStart.HandleBankFrame.SkipLeft + 1), A
                RET

                endmodule
                endmodule
