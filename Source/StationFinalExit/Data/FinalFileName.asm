                module FinalFileName
                ; Документация [финальный переход](../../../Docs/FinalExit.md)
                assert $ == #405C
Entry:          FTrDosFileKey { { "FINALF  " }, #43 }                           ; Name восемь байтов, Extension=C, терминатора нет
                assert $ == #4065
                endmodule
