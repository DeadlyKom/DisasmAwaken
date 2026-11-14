                module ArchiveEngine
                module InitializeMeters
                ; Документация [экранные индикаторы](../../Docs/ArchiveEngineMeters.md)
                ; -----------------------------------------
                ; настройка целей заполнения и вывод исходных рамок индикаторов
                ; In:
                ;   селектор страниц настроен, экран страницы 7 доступен
                ; Out:
                ;   обе цели равны 120, два диапазона атрибутов равны #14
                ;   экранные полосы содержат исходные рамки и надпись, выбрана страница 7
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; Note:
                ;   счётчики заполнения, адреса и маски продолжают использовать исходную физическую запись
                ; -----------------------------------------
                ; установка предела заполнения обеих полос
Entry:          LD A, @ArchiveEngineConst.MeterFull
                LD (@ArchiveEngineMeters.Value.LeftTarget), A
                LD (@ArchiveEngineMeters.Value.RightTarget), A
                LD A, @ArchiveEngineConst.ScreenPage
                CALL @ArchiveEngine.SelectPage.Entry

                ; заполнение атрибутов левого и правого индикаторов
                LD HL, @ArchiveEngineConst.MeterAttrLeft
                LD D, H
                LD E, L
                INC DE
                LD BC, @ArchiveEngineConst.MeterTail
                LD (HL), @ArchiveEngineConst.MeterAttribute
                LDIR
                LD HL, @ArchiveEngineConst.MeterAttrRight
                LD D, H
                LD E, L
                INC DE
                LD BC, @ArchiveEngineConst.MeterTail
                LD (HL), @ArchiveEngineConst.MeterAttribute
                LDIR

                ; перенос исходных растров на теневой экран
                LD HL, @ArchiveEngineMeterImages.Left
                LD DE, @ArchiveEngineConst.MeterLeftTop
                CALL @ArchiveEngine.CopyMeterBitmap.Entry
                LD HL, @ArchiveEngineMeterImages.Right
                LD DE, @ArchiveEngineConst.MeterRightTop
                CALL @ArchiveEngine.CopyMeterBitmap.Entry
                RET

                endmodule
                endmodule
