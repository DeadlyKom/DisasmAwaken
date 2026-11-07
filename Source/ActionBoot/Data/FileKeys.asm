                module ActionBootFileKeys
                ; Документация [ключи загрузчика полёта](../../../Docs/ActionBootFileKeys.md)
                assert $ == #42D0
Voxal:          FTrDosFileKey { { "VOXAL   " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
Voxal0:         FTrDosFileKey { { "VOXAL0  " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
Control:        FTrDosFileKey { { "CONTROL " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
Control0:       FTrDosFileKey { { "CONTROL0" }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
Panel:          FTrDosFileKey { { "PANEL   " }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
Object3D:       FTrDosFileKey { { "OBJECT3D" }, #43 }                           ; восемь символов имени с исходными пробелами и тип C, терминатора нет
                assert $ == #4306
                endmodule
