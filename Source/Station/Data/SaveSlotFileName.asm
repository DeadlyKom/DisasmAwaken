                module SaveSlotFileName
                ; Документация [сохранения слотов](../../../Docs/SaveSlots.md)
                ; проверка исходного адреса физического ключа SAVE
                assert $ == #7530
Entry:          FTrDosFileKey { { "SAVE1   " }, #73 }                           ; Name содержит SAVE, цифру и три пробела, Extension=s
                ; проверка конца девятибайтового имени и типа
                assert $ == #7539
                endmodule
