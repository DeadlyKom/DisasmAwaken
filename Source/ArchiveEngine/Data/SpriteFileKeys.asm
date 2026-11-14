                module ArchiveBdKeys
                ; Документация [ключи файлов масок](../../../Docs/FighterAssets.md#вывод-и-чтение-секторов)
Bd0:            FTrDosFileKey { { "BD0     " }, #43 }                           ; маски страницы 8
Bd1:            FTrDosFileKey { { "BD1     " }, #43 }                           ; маски страницы 9
Bd2:            FTrDosFileKey { { "BD2     " }, #43 }                           ; маски страницы 10
Bd3:            FTrDosFileKey { { "BD3     " }, #43 }                           ; маски страницы 11

                ; Побайтовая копия первой таблицы, чтений при проверенной загрузке и первых 32 кадрах нет.
Bd0Copy:        FTrDosFileKey { { "BD0     " }, #43 }                           ; повтор ключа страницы 8
Bd1Copy:        FTrDosFileKey { { "BD1     " }, #43 }                           ; повтор ключа страницы 9
Bd2Copy:        FTrDosFileKey { { "BD2     " }, #43 }                           ; повтор ключа страницы 10
Bd3Copy:        FTrDosFileKey { { "BD3     " }, #43 }                           ; повтор ключа страницы 11
                endmodule
