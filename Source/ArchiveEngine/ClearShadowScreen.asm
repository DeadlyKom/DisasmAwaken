                module ArchiveEngine
                module ClearShadowScreen
                ; Документация [запуск и цикл ENGINE](../../Docs/ArchiveEngineStartup.md)
                ; -----------------------------------------
                ; очистка растра и атрибутов теневого экрана
                ; In:
                ;   операнд SelectPage.Dispatch настроен, теневой экран доступен в странице 7
                ; Out:
                ;   HL - #DAFF, последний атрибут, DE - #DB00, BC - 0
                ;   окно #C000 выбрано на страницу 7, растр нулевой, атрибуты равны #07
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
Entry:          LD A, @ArchiveEngineConst.ScreenPage
                CALL @ArchiveEngine.SelectPage.Entry

                ; заполнение растра и первого байта атрибутов одним перекрывающимся переносом
                LD HL, @ArchiveEngineConst.ScreenBitmap
                LD D, H
                LD E, L
                INC DE
                LD (HL), #00
                LD BC, @ArchiveEngineConst.BitmapSize
                LDIR

                ; установка первого атрибута и его размножение до конца экрана
                LD (HL), @ArchiveEngineConst.EmptyAttribute
                LD BC, @ArchiveEngineConst.AttributeTail
                LDIR
                RET

                endmodule
                endmodule
