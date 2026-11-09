                module StationBootFileKeys
                ; Документация [ключи загрузчика станции](../../../Docs/StationBootResourceTables.md)
                assert $ == #402A
Karta:          FTrDosFileKey { { "KARTA   " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
Muz1:           FTrDosFileKey { { "MUZ1    " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
StationScreens: FTrDosFileKey { { "stscr   " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
Help:           FTrDosFileKey { { "HELP    " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
D3D:            FTrDosFileKey { { "D3D     " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
Lang:           FTrDosFileKey { { "LANG    " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
                assert $ == #4060
                endmodule
