                module ActionFileName
; Документация [выход станции](../../../Docs/StationExit.md)
                assert $ == #4248
Entry:          FTrDosFileKey { { "ACTION  " }, #43 }                           ; Name из восьми байтов, Extension=C, терминатора нет
                assert $ == #4251
                endmodule
