                module SettingsText
; Документация [изменяемые подписи](../../../Docs/SettingsLabels.md)
; исходные тексты до FormatSettingsLabel, загрузчик заменяет их по длине до нуля
                assert $ == #9728
Interface:      db "YNYNQAOP M040", #00
                assert $ == #9736
Controls:       db "YSXKLNMA ", #1F, "PHC123JFZRBQWEGDTVSXKLA ", #1F
                db "PHC1JQDB", #00
                assert $ == #9762
                endmodule
