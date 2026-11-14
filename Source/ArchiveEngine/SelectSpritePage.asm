                module ArchiveEngine
                module SelectSpritePage
                ; Документация [выбор страниц](../../Docs/ArchiveEnginePaging.md)
                ; -----------------------------------------
                ; выбор страницы по индексу одного из четырёх файлов BD
                ; In:
                ;   AF - A, индекс 0..3
                ; Out:
                ;   HL - адрес прочитанного кода, DE - начало таблицы кодов
                ;   AF - результат SelectPage для кода 8..11, BC сохранён
                ; Corrupt:
                ;   HL, DE, AF, отображение банкового окна
                ; -----------------------------------------
                ; преобразование индекса BD в логический код страницы
Entry:          LD L, A
                LD H, #00
                LD DE, @ArchiveEnginePages.SpriteCodes
                ADD HL, DE
                LD A, (HL)
                CALL @ArchiveEngine.SelectPage.Entry
                RET

                endmodule
                endmodule
