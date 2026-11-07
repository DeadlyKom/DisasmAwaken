                module BasicProgramPrefix
                ; Документация [исходная BASIC-программа](../../../Docs/BasicProgram.md)
                assert $ == #5D3B
Line10:         FBasicLineHeader { #00, #0A, #0061 }
Remark:         db #20, #EA                                                     ; пробел и REM перед исходными 24 байтами Z80
                assert $ == #5D41
                endmodule
