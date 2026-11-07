                module ActionDiagnosticMessages
                ; Документация [диагностическая очередь](../../../Docs/ActionDiagnosticQueue.md)
                assert $ == #ACD6
StatusText:     db "Status: ", #0A                                              ; заголовок первого числа и LF, строка не завершается нулём
DeadsText:      db #0D, "Deads: ", #0A                                          ; CR, заголовок двух следующих чисел и LF
NewLine:        db #0D, #0A                                                     ; отдельные CR и LF
                assert $ == #ACEA
                endmodule
